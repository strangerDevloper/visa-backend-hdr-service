from sqlalchemy.orm import Session
from datetime import datetime
from app.models.coupon import Coupon
from app.api.coupon.coupon_types import CouponCreate, CouponUpdate

def create_coupon(db: Session, coupon: CouponCreate):
    db_coupon = Coupon(
        coupon_code=coupon.coupon_code,
        discount_type=coupon.discount_type,
        discount_value=coupon.discount_value,
        start_date=coupon.start_date,
        expire_date=coupon.expire_date,
        max_uses=coupon.max_uses,
        min_purchase_amount=coupon.min_purchase_amount,
        is_active=coupon.is_active,
        created_by=coupon.created_by,
        description=coupon.description
    )
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def get_coupon(db: Session, coupon_id: int):
    return db.query(Coupon).filter(Coupon.coupon_id == coupon_id).first()

def get_coupon_by_code(db: Session, coupon_code: str):
    return db.query(Coupon).filter(Coupon.coupon_code == coupon_code).first()

def get_coupons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Coupon).offset(skip).limit(limit).all()

def update_coupon(db: Session, coupon_id: int, coupon: CouponUpdate):
    db_coupon = db.query(Coupon).filter(Coupon.coupon_id == coupon_id).first()
    if not db_coupon:
        return None
    
    update_data = coupon.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_coupon, field, value)
    
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def deactivate_coupon(db: Session, coupon_id: int):
    db_coupon = db.query(Coupon).filter(Coupon.coupon_id == coupon_id).first()
    if not db_coupon:
        return False
    
    db_coupon.is_active = False
    db.commit()
    db.refresh(db_coupon)
    return True

def validate_coupon(db: Session, coupon_code: str, purchase_amount: float):
    coupon = get_coupon_by_code(db, coupon_code)
    if not coupon:
        return {"valid": False, "message": "Coupon not found"}
    
    now = datetime.utcnow()
    if now < coupon.start_date:
        return {"valid": False, "message": "Coupon not yet valid"}
    
    if now > coupon.expire_date:
        return {"valid": False, "message": "Coupon has expired"}
    
    if not coupon.is_active:
        return {"valid": False, "message": "Coupon is inactive"}
    
    if coupon.current_uses >= coupon.max_uses:
        return {"valid": False, "message": "Coupon usage limit reached"}
    
    if purchase_amount < coupon.min_purchase_amount:
        return {
            "valid": False,
            "message": f"Minimum purchase amount {coupon.min_purchase_amount} required"
        }
    
    # Calculate discount
    if coupon.discount_type == "FLAT":
        discount = min(coupon.discount_value, purchase_amount)
    else:  # PERCENTAGE
        discount = purchase_amount * (coupon.discount_value / 100)
    
    return {
        "valid": True,
        "discount_amount": discount,
        "final_amount": purchase_amount - discount,
        "coupon": coupon
    }

def apply_coupon(db: Session, coupon_code: str, purchase_amount: float):
    validation = validate_coupon(db, coupon_code, purchase_amount)
    if not validation["valid"]:
        return validation
    
    coupon = validation["coupon"]
    coupon.current_uses += 1
    db.commit()
    db.refresh(coupon)
    
    validation["message"] = "Coupon applied successfully"
    return validation