from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.restaurant import Restaurant, MenuItem
from app.models.food_order import FoodOrder, OrderItem, OrderStatus
from app.models.review import Review, TargetType
from app.schemas.food_order import FoodOrderCreate, FoodOrderResponse
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/api/orders/food", tags=["Food Orders"])


@router.post("", response_model=FoodOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_food_order(
    order_data: FoodOrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new food order"""
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == order_data.restaurant_id).first()
    if not restaurant or not restaurant.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found or inactive"
        )

    # Calculate order totals
    subtotal = Decimal("0.0")
    order_items_to_create = []

    for item in order_data.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item or not menu_item.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item {item.menu_item_id} not available"
            )

        item_total = menu_item.price * item.quantity
        subtotal += item_total
        order_items_to_create.append({
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity,
            "unit_price": menu_item.price,
            "total_price": item_total,
            "special_instructions": item.special_instructions
        })

    # Calculate tax and total
    delivery_fee = restaurant.delivery_fee
    tax = subtotal * Decimal("0.08")  # 8% tax
    total_amount = subtotal + delivery_fee + tax

    # Create order
    new_order = FoodOrder(
        customer_id=current_user.id,
        restaurant_id=order_data.restaurant_id,
        delivery_address=order_data.delivery_address,
        delivery_latitude=order_data.delivery_latitude,
        delivery_longitude=order_data.delivery_longitude,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax=tax,
        total_amount=total_amount,
        special_instructions=order_data.special_instructions,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    db.flush()

    # Create order items
    for item_data in order_items_to_create:
        order_item = OrderItem(order_id=new_order.id, **item_data)
        db.add(order_item)

    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("", response_model=List[FoodOrderResponse])
async def list_user_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List current user's food orders"""
    orders = db.query(FoodOrder).filter(
        FoodOrder.customer_id == current_user.id
    ).order_by(FoodOrder.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=FoodOrderResponse)
async def get_order_details(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific food order details"""
    order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Ensure user owns the order or is a driver/admin
    if order.customer_id != current_user.id and current_user.role.value not in ["driver", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )

    return order


@router.put("/{order_id}/cancel")
async def cancel_order(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a food order"""
    order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Ensure user owns the order
    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )

    # Can only cancel if order is pending or confirmed
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status: {order.status.value}"
        )

    order.status = OrderStatus.CANCELLED
    db.commit()

    return {"message": "Order cancelled successfully", "order_id": str(order_id)}


@router.post("/{order_id}/review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def review_restaurant(
    order_id: UUID,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add review for restaurant after order is delivered"""
    order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Ensure user owns the order
    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to review this order"
        )

    # Can only review delivered orders
    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review delivered orders"
        )

    # Check if already reviewed
    existing_review = db.query(Review).filter(
        Review.order_id == order_id,
        Review.reviewer_id == current_user.id,
        Review.target_type == TargetType.RESTAURANT
    ).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already reviewed"
        )

    # Create review
    review = Review(
        reviewer_id=current_user.id,
        target_type=TargetType.RESTAURANT,
        target_id=order.restaurant_id,
        order_id=order_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Update restaurant rating average
    restaurant_reviews = db.query(Review).filter(
        Review.target_type == TargetType.RESTAURANT,
        Review.target_id == order.restaurant_id
    ).all()
    if restaurant_reviews:
        avg_rating = sum(r.rating for r in restaurant_reviews) / len(restaurant_reviews)
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
        restaurant.rating_average = avg_rating
        db.commit()

    return review
