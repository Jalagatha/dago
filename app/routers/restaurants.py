from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.restaurant import Restaurant, MenuItem, MenuCategory
from app.schemas.restaurant import (
    RestaurantResponse,
    RestaurantWithMenu,
    MenuItemResponse
)

router = APIRouter(prefix="/api/restaurants", tags=["Restaurants"])


@router.get("", response_model=List[RestaurantResponse])
async def list_restaurants(
    cuisine_type: Optional[str] = None,
    city: Optional[str] = None,
    is_active: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db)
):
    """List all restaurants with optional filters"""
    query = db.query(Restaurant)

    if cuisine_type:
        query = query.filter(Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))
    if is_active is not None:
        query = query.filter(Restaurant.is_active == is_active)

    restaurants = query.offset(skip).limit(limit).all()
    return restaurants


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(restaurant_id: UUID, db: Session = Depends(get_db)):
    """Get restaurant details"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=RestaurantWithMenu)
async def get_restaurant_menu(restaurant_id: UUID, db: Session = Depends(get_db)):
    """Get restaurant menu with categories and items"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    return restaurant


@router.get("/menu-items/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(item_id: UUID, db: Session = Depends(get_db)):
    """Get specific menu item details"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return menu_item


@router.get("/{restaurant_id}/reviews")
async def get_restaurant_reviews(
    restaurant_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get restaurant reviews"""
    from app.models.review import Review, TargetType

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    reviews = db.query(Review).filter(
        Review.target_type == TargetType.RESTAURANT,
        Review.target_id == restaurant_id
    ).offset(skip).limit(limit).all()

    return reviews
