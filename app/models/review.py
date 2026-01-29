from sqlalchemy import Column, String, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime
import uuid
import enum
from app.core.database import Base


class TargetType(str, enum.Enum):
    RESTAURANT = "restaurant"
    DRIVER = "driver"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_type = Column(SQLEnum(TargetType), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)  # Can reference restaurant or driver
    order_id = Column(UUID(as_uuid=True), nullable=True)  # References either food_orders or parcel_deliveries
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviewer = relationship("User", back_populates="reviews_given", foreign_keys=[reviewer_id])
