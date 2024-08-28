from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.api.schemas import user
from app.core.otp_utils import generate_otp, send_otp_email, temporary_user_store
import uuid


async def get_users(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users


async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
async def update_user(user_id: int, user: user.UserUpdate, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User).filter(User.id == user_id))
        db_user = result.scalars().first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.username != db_user.username:
            existing_user = await session.execute(select(User).filter(User.username == user.username))
            if existing_user.scalars().first():
                raise HTTPException(status_code=400, detail="Username already in use")
        
        if user.email != db_user.email:
            existing_user = await session.execute(select(User).filter(User.email == user.email))
            if existing_user.scalars().first():
                raise HTTPException(status_code=400, detail="Email already in use")
            
            otp = generate_otp()
            temp_user_id = str(uuid.uuid4())
            temporary_user_store[temp_user_id] = {
                "user_id": user_id,
                "user_name": user.username,
                "new_email": user.email,
                "otp": otp,
                "type": "email_update"
            }
            await send_otp_email(user.email, otp)

            return {"message": "OTP sent to your email. Please verify.", "temp_user_id": temp_user_id}
            
        

        for key, value in user.dict().items():
            setattr(db_user, key, value)
        await session.commit()
        await session.refresh(db_user)
        
        return {
            "username": db_user.username,
            "email": db_user.email
        }

    
async def delete_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # Fetch user by ID
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Fetch and delete all transactions associated with the user
        transaction_result = await session.execute(select(Transaction).filter(Transaction.user_id == user.id))
        transactions = transaction_result.scalars().all()
        
        # Delete the user and their transactions
        for transaction in transactions:
            await session.delete(transaction)
        
        await session.delete(user)
        await session.commit()

        return {
            "status": "success",
            "message": f"User {user.username} and his transactions have been deleted successfully."
        }

async def update_user_role(user_id: int, role: str, db: AsyncSession) -> User:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if user:
        user.role = role
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
