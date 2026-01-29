from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.parcel import ParcelSize, ParcelStatus


class ParcelDeliveryCreate(BaseModel):
    recipient_name: str
    recipient_phone: str
    pickup_address: str
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    delivery_address: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    parcel_description: Optional[str] = None
    parcel_size: ParcelSize = ParcelSize.SMALL
    weight_kg: Optional[float] = None


class ParcelDeliveryUpdate(BaseModel):
    status: Optional[ParcelStatus] = None
    driver_id: Optional[UUID] = None


class ParcelDeliveryResponse(BaseModel):
    id: UUID
    sender_id: UUID
    driver_id: Optional[UUID] = None
    recipient_name: str
    recipient_phone: str
    pickup_address: str
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    delivery_address: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    parcel_description: Optional[str] = None
    parcel_size: ParcelSize
    weight_kg: Optional[float] = None
    status: ParcelStatus
    delivery_fee: Decimal
    estimated_distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
