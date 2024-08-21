from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import transaction,  user as userSchema
from app.services import user as userRepo
from app.core.database import get_db

router = APIRouter()

@router.get("/{user_id}", response_model=transaction.ShowUser)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await userRepo.get_user(user_id, db)

@router.get("/", response_model=List[transaction.ShowUser])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    return await userRepo.get_users(db)

@router.put("/{user_id}", response_model=transaction.ShowUser)
async def update_user(
    user_id: int,
    user: userSchema.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await userRepo.update_user(user_id, user, db)

@router.delete("/{user_id}", response_model=userSchema.DeleteUserResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await userRepo.delete_user_by_id(user_id, db)

@router.put("/{user_id}/role", response_model=transaction.ShowUser)
async def update_user_role(
    user_id: int,
    role_update: userSchema.RoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    role = role_update.role
    # Ensure the role is valid
    if role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Get the user from the database
    user = await userRepo.get_user(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's role
    updated_user = await userRepo.update_user_role(user_id, role, db)
    return updated_user