from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.food_order import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity: int
    special_instructions: Optional[str] = None


class OrderItemResponse(OrderItemCreate):
    id: UUID
    order_id: UUID
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True


class FoodOrderCreate(BaseModel):
    restaurant_id: UUID
    delivery_address: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    special_instructions: Optional[str] = None
    items: List[OrderItemCreate]


class FoodOrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    driver_id: Optional[UUID] = None


class FoodOrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    restaurant_id: UUID
    driver_id: Optional[UUID] = None
    status: OrderStatus
    delivery_address: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    subtotal: Decimal
    delivery_fee: Decimal
    tax: Decimal
    total_amount: Decimal
    special_instructions: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
