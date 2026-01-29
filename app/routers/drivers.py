from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User, UserRole, DriverProfile
from app.models.food_order import FoodOrder, OrderStatus
from app.models.parcel import ParcelDelivery, ParcelStatus
from app.schemas.food_order import FoodOrderResponse
from app.schemas.parcel import ParcelDeliveryResponse

router = APIRouter(prefix="/api/driver", tags=["Driver"])


@router.get("/available-orders", response_model=List[FoodOrderResponse])
async def get_available_food_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Get available food orders for drivers to accept"""
    orders = db.query(FoodOrder).filter(
        FoodOrder.driver_id.is_(None),
        FoodOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.READY])
    ).order_by(FoodOrder.created_at).offset(skip).limit(limit).all()
    return orders


@router.get("/available-parcels", response_model=List[ParcelDeliveryResponse])
async def get_available_parcels(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Get available parcel deliveries for drivers to accept"""
    parcels = db.query(ParcelDelivery).filter(
        ParcelDelivery.driver_id.is_(None),
        ParcelDelivery.status == ParcelStatus.PENDING
    ).order_by(ParcelDelivery.created_at).offset(skip).limit(limit).all()
    return parcels


@router.post("/accept/food/{order_id}")
async def accept_food_order(
    order_id: UUID,
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Accept a food order"""
    order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.driver_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already assigned to a driver"
        )

    order.driver_id = current_user.id
    if order.status == OrderStatus.CONFIRMED:
        order.status = OrderStatus.PREPARING
    db.commit()

    return {"message": "Order accepted successfully", "order_id": str(order_id)}


@router.post("/accept/parcel/{parcel_id}")
async def accept_parcel(
    parcel_id: UUID,
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Accept a parcel delivery"""
    parcel = db.query(ParcelDelivery).filter(ParcelDelivery.id == parcel_id).first()
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found"
        )

    if parcel.driver_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parcel already assigned to a driver"
        )

    parcel.driver_id = current_user.id
    parcel.status = ParcelStatus.ASSIGNED
    db.commit()

    return {"message": "Parcel accepted successfully", "parcel_id": str(parcel_id)}


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    new_status: OrderStatus,
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Update food order status"""
    order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this order"
        )

    order.status = new_status
    if new_status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()

        # Update driver's total deliveries
        driver_profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
        if driver_profile:
            driver_profile.total_deliveries += 1

    db.commit()

    return {"message": "Order status updated successfully", "order_id": str(order_id), "status": new_status.value}


@router.put("/parcels/{parcel_id}/status")
async def update_parcel_status(
    parcel_id: UUID,
    new_status: ParcelStatus,
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Update parcel delivery status"""
    parcel = db.query(ParcelDelivery).filter(ParcelDelivery.id == parcel_id).first()
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found"
        )

    if parcel.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this parcel"
        )

    parcel.status = new_status
    if new_status == ParcelStatus.PICKED_UP:
        parcel.picked_up_at = datetime.utcnow()
    elif new_status == ParcelStatus.DELIVERED:
        parcel.delivered_at = datetime.utcnow()

        # Update driver's total deliveries
        driver_profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
        if driver_profile:
            driver_profile.total_deliveries += 1

    db.commit()

    return {"message": "Parcel status updated successfully", "parcel_id": str(parcel_id), "status": new_status.value}


@router.get("/current-deliveries")
async def get_current_deliveries(
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Get driver's active deliveries"""
    food_orders = db.query(FoodOrder).filter(
        FoodOrder.driver_id == current_user.id,
        FoodOrder.status.in_([OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.PICKED_UP])
    ).all()

    parcels = db.query(ParcelDelivery).filter(
        ParcelDelivery.driver_id == current_user.id,
        ParcelDelivery.status.in_([ParcelStatus.ASSIGNED, ParcelStatus.PICKED_UP, ParcelStatus.IN_TRANSIT])
    ).all()

    return {
        "food_orders": food_orders,
        "parcels": parcels
    }


@router.put("/availability")
async def update_availability(
    is_available: bool,
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Toggle driver availability"""
    driver_profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )

    driver_profile.is_available = is_available
    db.commit()

    return {"message": "Availability updated successfully", "is_available": is_available}


@router.put("/location")
async def update_location(
    latitude: float,
    longitude: float,
    current_user: User = Depends(require_role([UserRole.DRIVER])),
    db: Session = Depends(get_db)
):
    """Update driver's current location"""
    driver_profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )

    driver_profile.current_latitude = latitude
    driver_profile.current_longitude = longitude
    db.commit()

    return {"message": "Location updated successfully"}
