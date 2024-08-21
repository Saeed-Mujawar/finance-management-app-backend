from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str
    email: str
    password: str
    class Config:
        orm_mode = True

class User(UserBase):
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: str
    email: str
    class Config:
        orm_mode = True

class RoleUpdate(BaseModel):
    role: str

class DeleteUserRequest(BaseModel):
    id: int
    class Config:
        orm_mode = True

class DeleteUserResponse(BaseModel):
    status: str
    message: str
    class Config:
        orm_mode = True
