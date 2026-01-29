from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant, MenuCategory, MenuItem
from app.models.food_order import FoodOrder
from app.models.parcel import ParcelDelivery
from app.models.review import Review
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse, MenuItemCreate, MenuCategoryCreate
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# User Management
@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    role: UserRole = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """List all users with optional role filter"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    is_verified: bool = None,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update user details (verify, suspend, etc.)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if is_verified is not None:
        user.is_verified = is_verified

    db.commit()

    return {"message": "User updated successfully", "user_id": str(user_id)}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully", "user_id": str(user_id)}


# Restaurant Management
@router.post("/restaurants", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create a new restaurant"""
    restaurant = Restaurant(**restaurant_data.dict())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.put("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: UUID,
    restaurant_data: RestaurantUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update restaurant details"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    for field, value in restaurant_data.dict(exclude_unset=True).items():
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete a restaurant"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    db.delete(restaurant)
    db.commit()

    return {"message": "Restaurant deleted successfully", "restaurant_id": str(restaurant_id)}


# Menu Management
@router.post("/restaurants/{restaurant_id}/categories")
async def create_menu_category(
    restaurant_id: UUID,
    category_data: MenuCategoryCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create menu category for a restaurant"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    category = MenuCategory(restaurant_id=restaurant_id, **category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.post("/restaurants/{restaurant_id}/menu-items")
async def create_menu_item(
    restaurant_id: UUID,
    item_data: MenuItemCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create menu item for a restaurant"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    menu_item = MenuItem(restaurant_id=restaurant_id, **item_data.dict())
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item


# Orders Management
@router.get("/orders")
async def list_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """View all food orders"""
    orders = db.query(FoodOrder).order_by(FoodOrder.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/parcels")
async def list_all_parcels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """View all parcel deliveries"""
    parcels = db.query(ParcelDelivery).order_by(ParcelDelivery.created_at.desc()).offset(skip).limit(limit).all()
    return parcels


# Review Management
@router.get("/reviews")
async def list_all_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """View all reviews"""
    reviews = db.query(Review).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    return reviews


@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete inappropriate review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    db.delete(review)
    db.commit()

    return {"message": "Review deleted successfully", "review_id": str(review_id)}
