from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
import math

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.parcel import ParcelDelivery, ParcelStatus, ParcelSize
from app.models.review import Review, TargetType
from app.schemas.parcel import ParcelDeliveryCreate, ParcelDeliveryResponse
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/api/deliveries/parcel", tags=["Parcel Deliveries"])


def calculate_delivery_fee(distance_km: float, parcel_size: ParcelSize) -> Decimal:
    """Calculate delivery fee based on distance and parcel size"""
    base_fee = Decimal("5.0")
    distance_fee = Decimal(str(distance_km)) * Decimal("2.0")

    size_multiplier = {
        ParcelSize.SMALL: Decimal("1.0"),
        ParcelSize.MEDIUM: Decimal("1.5"),
        ParcelSize.LARGE: Decimal("2.0")
    }

    total_fee = (base_fee + distance_fee) * size_multiplier[parcel_size]
    return total_fee


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km"""
    # Simplified distance calculation (Haversine formula)
    R = 6371  # Earth's radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


@router.post("", response_model=ParcelDeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_parcel_delivery(
    parcel_data: ParcelDeliveryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new parcel delivery request"""
    # Calculate distance if coordinates provided
    distance_km = 0.0
    if all([parcel_data.pickup_latitude, parcel_data.pickup_longitude,
            parcel_data.delivery_latitude, parcel_data.delivery_longitude]):
        distance_km = calculate_distance(
            parcel_data.pickup_latitude, parcel_data.pickup_longitude,
            parcel_data.delivery_latitude, parcel_data.delivery_longitude
        )
    else:
        # Default distance estimate
        distance_km = 5.0

    # Calculate delivery fee
    delivery_fee = calculate_delivery_fee(distance_km, parcel_data.parcel_size)

    # Create parcel delivery
    parcel = ParcelDelivery(
        sender_id=current_user.id,
        recipient_name=parcel_data.recipient_name,
        recipient_phone=parcel_data.recipient_phone,
        pickup_address=parcel_data.pickup_address,
        pickup_latitude=parcel_data.pickup_latitude,
        pickup_longitude=parcel_data.pickup_longitude,
        delivery_address=parcel_data.delivery_address,
        delivery_latitude=parcel_data.delivery_latitude,
        delivery_longitude=parcel_data.delivery_longitude,
        parcel_description=parcel_data.parcel_description,
        parcel_size=parcel_data.parcel_size,
        weight_kg=parcel_data.weight_kg,
        delivery_fee=delivery_fee,
        estimated_distance_km=distance_km,
        status=ParcelStatus.PENDING
    )
    db.add(parcel)
    db.commit()
    db.refresh(parcel)
    return parcel


@router.get("", response_model=List[ParcelDeliveryResponse])
async def list_user_parcels(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List current user's parcel deliveries"""
    parcels = db.query(ParcelDelivery).filter(
        ParcelDelivery.sender_id == current_user.id
    ).order_by(ParcelDelivery.created_at.desc()).offset(skip).limit(limit).all()
    return parcels


@router.get("/{parcel_id}", response_model=ParcelDeliveryResponse)
async def get_parcel_details(
    parcel_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific parcel delivery details"""
    parcel = db.query(ParcelDelivery).filter(ParcelDelivery.id == parcel_id).first()
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel delivery not found"
        )

    # Ensure user owns the parcel or is a driver/admin
    if parcel.sender_id != current_user.id and current_user.role.value not in ["driver", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this parcel"
        )

    return parcel


@router.put("/{parcel_id}/cancel")
async def cancel_parcel(
    parcel_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a parcel delivery"""
    parcel = db.query(ParcelDelivery).filter(ParcelDelivery.id == parcel_id).first()
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel delivery not found"
        )

    # Ensure user owns the parcel
    if parcel.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this parcel"
        )

    # Can only cancel if pending or assigned
    if parcel.status not in [ParcelStatus.PENDING, ParcelStatus.ASSIGNED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel parcel with status: {parcel.status.value}"
        )

    parcel.status = ParcelStatus.CANCELLED
    db.commit()

    return {"message": "Parcel delivery cancelled successfully", "parcel_id": str(parcel_id)}


@router.post("/{parcel_id}/review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def review_driver(
    parcel_id: UUID,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add review for driver after parcel is delivered"""
    parcel = db.query(ParcelDelivery).filter(ParcelDelivery.id == parcel_id).first()
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel delivery not found"
        )

    # Ensure user owns the parcel
    if parcel.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to review this delivery"
        )

    # Can only review delivered parcels
    if parcel.status != ParcelStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review delivered parcels"
        )

    if not parcel.driver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No driver assigned to this delivery"
        )

    # Check if already reviewed
    existing_review = db.query(Review).filter(
        Review.order_id == parcel_id,
        Review.reviewer_id == current_user.id,
        Review.target_type == TargetType.DRIVER
    ).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery already reviewed"
        )

    # Create review
    review = Review(
        reviewer_id=current_user.id,
        target_type=TargetType.DRIVER,
        target_id=parcel.driver_id,
        order_id=parcel_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Update driver rating average
    from app.models.user import DriverProfile
    driver_reviews = db.query(Review).filter(
        Review.target_type == TargetType.DRIVER,
        Review.target_id == parcel.driver_id
    ).all()
    if driver_reviews:
        avg_rating = sum(r.rating for r in driver_reviews) / len(driver_reviews)
        driver_profile = db.query(DriverProfile).filter(DriverProfile.user_id == parcel.driver_id).first()
        if driver_profile:
            driver_profile.rating_average = avg_rating
            db.commit()

    return review
