from fastapi import APIRouter, Depends
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import user, authentication
from app.services import authentication as authenticationRepo

router = APIRouter()

@router.post("/signup")
async def signup(
    user: user.User, 
    db: AsyncSession = Depends(get_db)
):
    temp_user_id = await authenticationRepo.signup(user, db)
    return {"message": "OTP sent to your email. Please verify.", "temp_user_id": temp_user_id}
    
@router.post("/login", response_model=authentication.LoginResponse)
async def login(
    userData: authentication.UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    response = await authenticationRepo.login(userData, db)
    return response

@router.post("/verify-otp")
async def verify_otp(data: authentication.OTPVerificationRequest, 
                     db: AsyncSession = Depends(get_db)
):
    response = await authenticationRepo.verify_otp(data, db)
    return response


@router.post("/forgot-password")
async def forgot_password(request: authentication.ForgotPasswordRequest, 
                          db: AsyncSession = Depends(get_db)
):
    response = await authenticationRepo.forgot_password(request, db)
    return response

@router.post("/reset-password")
async def reset_password(data: authentication.ResetPasswordRequest, 
                         db: AsyncSession = Depends(get_db)
):
    response = await authenticationRepo.reset_password(data, db)
    return response