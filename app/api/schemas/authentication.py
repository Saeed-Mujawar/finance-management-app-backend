from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    id: int
    access_token: str
    token_type: str
    username: str
    email: str
    role: str

class OTPVerificationRequest(BaseModel):
    temp_user_id: str
    otp: str
