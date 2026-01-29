from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    is_available: bool = True
    preparation_time: int = 15


class MenuItemCreate(MenuItemBase):
    category_id: Optional[UUID] = None


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = None
    category_id: Optional[UUID] = None


class MenuItemResponse(MenuItemBase):
    id: UUID
    restaurant_id: UUID
    category_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuCategoryBase(BaseModel):
    name: str
    display_order: int = 0


class MenuCategoryCreate(MenuCategoryBase):
    pass


class MenuCategoryResponse(MenuCategoryBase):
    id: UUID
    restaurant_id: UUID
    menu_items: List[MenuItemResponse] = []

    class Config:
        from_attributes = True


class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    address: str
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone_number: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    delivery_fee: Decimal = Decimal("0.0")
    estimated_delivery_time: int = 30


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone_number: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    delivery_fee: Optional[Decimal] = None
    estimated_delivery_time: Optional[int] = None


class RestaurantResponse(RestaurantBase):
    id: UUID
    rating_average: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RestaurantWithMenu(RestaurantResponse):
    menu_categories: List[MenuCategoryResponse] = []

    class Config:
        from_attributes = True
