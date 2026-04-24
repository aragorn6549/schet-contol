from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.core.enums import UserRole


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    login: str
    password: str


class UserResponse(UserBase):
    id: int
    login: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProfileBase(BaseModel):
    full_name: str
    role: UserRole = UserRole.ENGINEER


class ProfileCreate(ProfileBase):
    user_id: int


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    login: Optional[str] = None
