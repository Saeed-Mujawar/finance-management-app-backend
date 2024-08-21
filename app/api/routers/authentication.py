from fastapi import APIRouter, Depends, HTTPException,status
from app.core import  token
from app.core.database import get_db
from app.core.hashing import Hash
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.schemas import user, authentication
from app.models.user import User
from app.core.otp_utils import generate_otp, send_otp_email
import uuid

router = APIRouter()

temporary_user_store = {}

@router.post("/signup")
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

    
    temp_user_id = str(uuid.uuid4())  # Generate a unique ID for temporary storage
    temporary_user_store[temp_user_id] = {
        "user_data": user,
        "otp": otp,
    }

    # Send OTP via email
    await send_otp_email(user.email, otp)

    return {"message": "OTP sent to your email. Please verify.", "temp_user_id": temp_user_id}
    
@router.post("/login", response_model=authentication.LoginResponse)
# async def login(request: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
async def login(userData: authentication.UserLogin, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User).filter(User.username == userData.username))
        user = result.scalars().first()

    if not user or not Hash.verify(userData.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = token.create_access_token(data={"sub": user.email})
    return {
        "id": user.id,
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

@router.post("/verify-otp")
async def verify_otp(data: authentication.OTPVerificationRequest, db: AsyncSession = Depends(get_db)):
    # Retrieve the temporary user data
    if data.temp_user_id not in temporary_user_store:
        raise HTTPException(status_code=400, detail="Invalid temporary user ID")

    temp_user_data = temporary_user_store[data.temp_user_id]

    # Check if the provided OTP matches
    if temp_user_data["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Store the user in the database
    user = temp_user_data["user_data"]
    hashed_password = Hash.bcrypt(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    
    async with db as session:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

    # Clear the temporary data
    del temporary_user_store[data.temp_user_id]

    return {"message": "Email verified and user registered successfully!"}

