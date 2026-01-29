from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.review import TargetType


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)  # Rating must be between 1 and 5
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: UUID
    reviewer_id: UUID
    target_type: TargetType
    target_id: UUID
    order_id: Optional[UUID] = None
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
