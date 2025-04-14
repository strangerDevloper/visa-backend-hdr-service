from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Any, Optional
from enum import Enum

class CouponTypeEnum(str, Enum):
    FLAT = "FLAT"
    PERCENTAGE = "PERCENTAGE"

class CouponBase(BaseModel):
    coupon_code: str = Field(..., min_length=4, max_length=50)
    discount_type: CouponTypeEnum
    discount_value: float = Field(..., gt=0)
    start_date: datetime
    expire_date: datetime
    max_uses: int = Field(..., gt=0)
    min_purchase_amount: float = Field(..., ge=0)
    is_active: bool = True
    description: Optional[str] = Field(None, max_length=255)

    @validator('expire_date')
    def validate_expire_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("Expire date must be after start date")
        return v

    class Config:
        from_attributes = True

class CouponResponse(BaseModel):
    coupon_id: int
    coupon_code: str
    discount_type: str
    discount_value: float
    start_date: datetime
    expire_date: datetime
    max_uses: int
    current_uses: int
    min_purchase_amount: float
    is_active: bool
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class CouponCreate(CouponBase):
    created_by: int  # User ID from auth token

class Coupon(CouponBase):
    coupon_id: int
    current_uses: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class CouponUpdate(BaseModel):
    is_active: Optional[bool] = None
    max_uses: Optional[int] = Field(None, gt=0)
    expire_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=255)

class CouponApplyRequest(BaseModel):
    coupon_code: str
    purchase_amount: float = Field(..., gt=0)

class CouponApplyResponse(BaseModel):
    valid: bool
    message: str
    discount_amount: Optional[float] = None
    final_amount: Optional[float] = None
    coupon: Optional[CouponResponse] = None  # Use the Pydantic model here