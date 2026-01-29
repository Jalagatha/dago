from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class DriverProfileBase(BaseModel):
    vehicle_type: Optional[str] = None
    license_number: Optional[str] = None


class DriverProfileUpdate(DriverProfileBase):
    is_available: Optional[bool] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None


class DriverProfileResponse(DriverProfileBase):
    id: UUID
    user_id: UUID
    is_available: bool
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    rating_average: float
    total_deliveries: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    phone_number: Optional[str] = None
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    full_name: Optional[str] = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class UserResponse(UserBase):
    id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None
    driver_profile: Optional[DriverProfileResponse] = None

    class Config:
        from_attributes = True
