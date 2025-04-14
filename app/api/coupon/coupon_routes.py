from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import CurrentEmployee
from app.config.database import get_db

from . import coupon_types, coupon_service


router = APIRouter(prefix="/coupons", tags=["coupons"])

@router.post("/", response_model=coupon_types.Coupon, status_code=201)
def create_coupon(
    coupon: coupon_types.CouponCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    """
    Create a new coupon
    - Requires admin privileges
    """
    coupon.created_by = current_employee.employee_id
    return coupon_service.create_coupon(db, coupon)

@router.get("/", response_model=List[coupon_types.Coupon])
def read_coupons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all coupons
    """
    return coupon_service.get_coupons(db, skip=skip, limit=limit)

@router.get("/{coupon_id}", response_model=coupon_types.Coupon)
def read_coupon(
    coupon_id: int,
    db: Session = Depends(get_db)
):
    """
    Get coupon by ID
    """
    db_coupon = coupon_service.get_coupon(db, coupon_id=coupon_id)
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return db_coupon

@router.put("/{coupon_id}", response_model=coupon_types.Coupon)
def update_coupon(
    coupon_id: int,
    coupon: coupon_types.CouponUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Update coupon information
    - Requires admin privileges
    """
    db_coupon = coupon_service.update_coupon(db, coupon_id=coupon_id, coupon=coupon)
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return db_coupon


@router.delete("/{coupon_id}", status_code=status.HTTP_200_OK)
def delete_coupon(
    coupon_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Deactivate a coupon
    - Requires admin privileges
    Returns:
        - 200 OK with success message when successful
        - 404 Not Found when coupon doesn't exist
    """
    if not coupon_service.deactivate_coupon(db, coupon_id=coupon_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    return {
        "status": "success",
        "message": "Coupon deactivated successfully",
        "coupon_id": coupon_id
    }


@router.post("/validate", response_model=coupon_types.CouponApplyResponse)
def validate_coupon(
    request: coupon_types.CouponApplyRequest,
    db: Session = Depends(get_db)
):
    """
    Validate and calculate coupon discount
    Returns:
        - 200 OK with discount details for valid coupons
        - 400 Bad Request with error message for invalid coupons
    """
    result = coupon_service.validate_coupon(db, request.coupon_code, request.purchase_amount)
    
    if not result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": result["message"],
                "valid": False,
                "discount_amount": None,
                "final_amount": None
            }
        )
    
    return result

@router.post("/apply", response_model=coupon_types.CouponApplyResponse)
def apply_coupon(
    request: coupon_types.CouponApplyRequest,
    db: Session = Depends(get_db)
):
    """
    Apply coupon and increment usage count
    Returns:
        - 200 OK with discount details when successful
        - 400 Bad Request when coupon is invalid
    """
    result = coupon_service.apply_coupon(db, request.coupon_code, request.purchase_amount)
    
    if not result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": result["message"],
                "valid": False,
                "discount_amount": None,
                "final_amount": None,
                "coupon": None
            }
        )
    
    return result
