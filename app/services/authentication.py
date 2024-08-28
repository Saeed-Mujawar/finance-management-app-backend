from fastapi import Depends, HTTPException,status
from app.core import  token
from app.core.database import get_db
from app.core.hashing import Hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.schemas import user, authentication
from app.models.user import User
from app.core.otp_utils import generate_otp, send_otp_email, temporary_user_store
import uuid

async def signup(user: user.User, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User).filter(User.username == user.username))
        existing_user = result.scalars().first()

        email_check = await session.execute(select(User).filter(User.email == user.email))
        existing_email = email_check.scalars().first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    otp = generate_otp()    
    temp_user_id = str(uuid.uuid4())  

    temporary_user_store[temp_user_id] = {
        "user_data": user,
        "otp": otp,
        "type": "signup"
    }

    await send_otp_email(user.email, otp)

    return temp_user_id

async def login(userData: authentication.LoginResponse, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User).filter(User.username == userData.username))
        user = result.scalars().first()

    if not user or not Hash.verify(userData.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = token.create_access_token(data={"sub": user.email})

    return {
        "id": user.id,
        "access_token":access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

async def verify_otp(data: authentication.OTPVerificationRequest, db: AsyncSession = Depends(get_db)):
    if data.temp_user_id not in temporary_user_store:
        raise HTTPException(status_code=400, detail="Invalid temporary user ID")

    temp_user_data = temporary_user_store[data.temp_user_id]

    if temp_user_data["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    async with db as session:
        if temp_user_data["type"] == "email_update":
            result = await session.execute(select(User).filter(User.id == temp_user_data["user_id"]))
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.email = temp_user_data["new_email"]
            session.add(user)
            await session.commit()
            await session.refresh(user)

            del temporary_user_store[data.temp_user_id]
            return {"message": "Email updated successfully"}

        elif temp_user_data["type"] == "signup":
            user = temp_user_data["user_data"]
            hashed_password = Hash.bcrypt(user.password)
            new_user = User(
                username=user.username,
                email=user.email,
                password=hashed_password
            )

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            del temporary_user_store[data.temp_user_id]
            return {"message": "Email verified and user registered successfully!"}

        else:
            raise HTTPException(status_code=400, detail="Unknown OTP verification type")
        
async def forgot_password(request: authentication.ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    email = request.email

    async with db as session:
        result = await session.execute(select(User).filter(User.email == email))
        user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="Email not registered")

    otp = generate_otp()
    temp_user_id = str(uuid.uuid4())
    temporary_user_store[temp_user_id] = {
        "email": email,
        "otp": otp,
        "type": "reset_password"
    }

    await send_otp_email(email, otp)

    return {
        "message": "OTP sent to your email. Please use it to reset your password.",
        "temp_user_id": temp_user_id
    }

async def reset_password(data: authentication.ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    if data.temp_user_id not in temporary_user_store:
        raise HTTPException(status_code=400, detail="Invalid temporary user ID")

    temp_user_data = temporary_user_store[data.temp_user_id]

    if temp_user_data["otp"] != data.otp or temp_user_data["type"] != "reset_password":
        raise HTTPException(status_code=400, detail="Invalid OTP")

    async with db as session:
        result = await session.execute(select(User).filter(User.email == temp_user_data["email"]))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        hashed_password = Hash.bcrypt(data.new_password)
        user.password = hashed_password
        session.add(user)
        await session.commit()
        await session.refresh(user)

    del temporary_user_store[data.temp_user_id]

    return {"message": "Password reset successfully"}