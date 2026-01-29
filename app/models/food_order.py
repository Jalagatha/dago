from sqlalchemy import Column, String, ForeignKey, Float, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime, Numeric
import uuid
import enum
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    subtotal = Column(Numeric(10, 2), nullable=False)
    delivery_fee = Column(Numeric(10, 2), default=0.0)
    tax = Column(Numeric(10, 2), default=0.0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    special_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("User", back_populates="food_orders", foreign_keys=[customer_id])
    restaurant = relationship("Restaurant", back_populates="food_orders")
    driver = relationship("User", foreign_keys=[driver_id])
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    reviews = relationship("Review", primaryjoin="FoodOrder.id==Review.order_id", foreign_keys="Review.order_id", viewonly=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("food_orders.id"), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    special_instructions = Column(Text, nullable=True)

    # Relationships
    order = relationship("FoodOrder", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")
