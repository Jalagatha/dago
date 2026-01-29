from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
