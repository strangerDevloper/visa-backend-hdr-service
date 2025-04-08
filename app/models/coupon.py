from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.config.database import Base
from enum import Enum as PyEnum

class CouponTypeEnum(str, PyEnum):
    FLAT = "FLAT"
    PERCENTAGE = "PERCENTAGE"

class Coupon(Base):
    __tablename__ = "coupons"

    coupon_id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(Enum(CouponTypeEnum), nullable=False)
    discount_value = Column(Numeric(10, 2), nullable=False)
    start_date = Column(DateTime, nullable=False)
    expire_date = Column(DateTime, nullable=False)
    max_uses = Column(Integer, nullable=False)
    current_uses = Column(Integer, default=0)
    min_purchase_amount = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, nullable=False)  # User ID who created the coupon
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Coupon {self.coupon_code}>"