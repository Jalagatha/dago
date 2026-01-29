from sqlalchemy import Column, String, ForeignKey, Float, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime, Numeric
import uuid
import enum
from app.core.database import Base


class ParcelSize(str, enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ParcelStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ParcelDelivery(Base):
    __tablename__ = "parcel_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    recipient_name = Column(String, nullable=False)
    recipient_phone = Column(String, nullable=False)
    pickup_address = Column(String, nullable=False)
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    delivery_address = Column(String, nullable=False)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    parcel_description = Column(Text, nullable=True)
    parcel_size = Column(SQLEnum(ParcelSize), default=ParcelSize.SMALL, nullable=False)
    weight_kg = Column(Float, nullable=True)
    status = Column(SQLEnum(ParcelStatus), default=ParcelStatus.PENDING, nullable=False)
    delivery_fee = Column(Numeric(10, 2), nullable=False)
    estimated_distance_km = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    sender = relationship("User", back_populates="parcel_deliveries", foreign_keys=[sender_id])
    driver = relationship("User", foreign_keys=[driver_id])
    reviews = relationship("Review", primaryjoin="ParcelDelivery.id==Review.order_id", foreign_keys="Review.order_id", viewonly=True)
