from sqlalchemy.orm import Session
from datetime import datetime
from app.models.coupon import Coupon
from app.api.coupon.coupon_types import CouponCreate, CouponResponse, CouponUpdate

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
    # Initialize response with all required fields
    base_response = {
        "valid": False,
        "message": "",
        "discount_amount": None,
        "final_amount": None,
        "coupon": None
    }
    
    coupon = get_coupon_by_code(db, coupon_code)
    if not coupon:
        base_response["message"] = "Coupon not found"
        return base_response
    
    now = datetime.utcnow()
    if now < coupon.start_date:
        base_response["message"] = "Coupon not yet valid"
        return base_response
    
    if now > coupon.expire_date:
        base_response["message"] = "Coupon has expired"
        return base_response
    
    if not coupon.is_active:
        base_response["message"] = "Coupon is inactive"
        return base_response
    
    if coupon.current_uses >= coupon.max_uses:
        base_response["message"] = "Coupon usage limit reached"
        return base_response
    
    min_purchase = float(coupon.min_purchase_amount)
    if purchase_amount < min_purchase:
        base_response["message"] = f"Minimum purchase amount {min_purchase} required"
        return base_response
    
    # Calculate discount for valid coupons
    discount_value = float(coupon.discount_value)
    if coupon.discount_type == "FLAT":
        discount = min(discount_value, purchase_amount)
    else:  # PERCENTAGE
        discount = purchase_amount * (discount_value / 100.0)
    
    return {
        "valid": True,
        "message": "Coupon is valid",
        "discount_amount": discount,
        "final_amount": purchase_amount - discount,
        "coupon": coupon
    }


# def apply_coupon(db: Session, coupon_code: str, purchase_amount: float):
#     validation = validate_coupon(db, coupon_code, purchase_amount)
#     if not validation["valid"]:
#         return validation
    
#     coupon = validation["coupon"]
#     coupon.current_uses += 1
    
#     try:
#         db.commit()
#         db.refresh(coupon)
#     except Exception as e:
#         db.rollback()
#         return {
#             "valid": False,
#             "message": f"Failed to apply coupon: {str(e)}",
#             "discount_amount": None,
#             "final_amount": None,
#             "coupon": None
#         }
    
#     # Convert SQLAlchemy model to Pydantic model
#     coupon_response = CouponResponse.model_validate(coupon)
    
#     return {
#         "valid": True,
#         "message": "Coupon applied successfully",
#         "discount_amount": validation["discount_amount"],
#         "final_amount": validation["final_amount"],
#         "coupon": coupon_response
#     }

# In coupon_service.py
def apply_coupon(db: Session, coupon_code: str, purchase_amount: float):
    # First validate the coupon
    validation = validate_coupon(db, coupon_code, purchase_amount)
    if not validation["valid"]:
        return {
            "valid": False,
            "message": validation["message"],
            "discount_amount": None,
            "final_amount": None,
            "coupon": None
        }
    
    coupon = validation["coupon"]
    
    try:
        # Increment usage count
        coupon.current_uses += 1
        db.commit()
        db.refresh(coupon)
        
        # Convert SQLAlchemy model to dict for proper serialization
        coupon_data = {
            "coupon_id": coupon.coupon_id,
            "coupon_code": coupon.coupon_code,
            "discount_type": coupon.discount_type,
            "discount_value": float(coupon.discount_value),
            "start_date": coupon.start_date,
            "expire_date": coupon.expire_date,
            "max_uses": coupon.max_uses,
            "current_uses": coupon.current_uses,
            "min_purchase_amount": float(coupon.min_purchase_amount),
            "is_active": coupon.is_active,
            "created_at": coupon.created_at,
            "created_by": coupon.created_by,
            "description": coupon.description
        }
        
        return {
            "valid": True,
            "message": "Coupon applied successfully",
            "discount_amount": validation["discount_amount"],
            "final_amount": validation["final_amount"],
            "coupon": coupon_data
        }
        
    except Exception as e:
        db.rollback()
        return {
            "valid": False,
            "message": f"Failed to apply coupon: {str(e)}",
            "discount_amount": None,
            "final_amount": None,
            "coupon": None
        }