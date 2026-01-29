from sqlalchemy import Column, String, Boolean, ForeignKey, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime, Numeric
import uuid
from app.core.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cuisine_type = Column(String, nullable=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone_number = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    rating_average = Column(Float, default=0.0)
    delivery_fee = Column(Numeric(10, 2), default=0.0)
    estimated_delivery_time = Column(Integer, default=30)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    menu_categories = relationship("MenuCategory", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    food_orders = relationship("FoodOrder", back_populates="restaurant")
    reviews = relationship("Review", primaryjoin="and_(Restaurant.id==Review.target_id, Review.target_type=='restaurant')", foreign_keys="Review.target_id", viewonly=True)


class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    display_order = Column(Integer, default=0)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_categories")
    menu_items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("menu_categories.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    preparation_time = Column(Integer, default=15)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    category = relationship("MenuCategory", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
