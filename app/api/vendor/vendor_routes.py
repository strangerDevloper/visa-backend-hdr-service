# app/api/vendor/vendor_routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.constants import USER_TYPE_VENDOR
from app.helpers import auth_utils
from ..dependencies import CurrentEmployee, CurrentVendor  # Updated imports
from . import vendor_service
from .vendor_types import (
    VendorSignup,
    VendorSignupResponse,
    VendorToken,
    VendorPublic,
    VendorProfileUpdate,
    VendorApprove
)

router = APIRouter(prefix="/vendors", tags=["vendors"])

@router.post("/signup", response_model=VendorSignupResponse)
def signup_vendor(vendor: VendorSignup, db: Session = Depends(get_db)):
    db_vendor = vendor_service.get_vendor_by_email(db, vendor.email)
    if db_vendor:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_vendor = vendor_service.create_vendor(db, vendor)
    return VendorSignupResponse(
        vendor_id=new_vendor.vendor_id,
        email=new_vendor.email,
        status=new_vendor.status
    )

@router.post("/signin", response_model=VendorToken)
def signin_vendor(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_vendor = vendor_service.get_vendor_by_email(db, form_data.username)
    if not db_vendor or not db_vendor.password_hash:
        raise HTTPException(status_code=401, detail="Account not approved or invalid email")
    
    if not auth_utils.verify_password(form_data.password, db_vendor.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    if db_vendor.status != "APPROVED":
        raise HTTPException(status_code=403, detail="Account not approved yet")
    
    access_token = auth_utils.create_access_token(
        data={"sub": str(db_vendor.vendor_id)},
        user_type=USER_TYPE_VENDOR
    )
    vendor_service.update_login_info(db, db_vendor.vendor_id)
    return VendorToken(access_token=access_token)

@router.post("/approve", response_model=VendorPublic)
def approve_vendor(
    approval: VendorApprove,
    current_employee: CurrentEmployee,  # Only employees can access
    db: Session = Depends(get_db),
):
    
    if not current_employee.employee_id:
        raise HTTPException(status_code=403, detail="Not authorized to approve vendors")
    
    approved_vendor = vendor_service.approve_vendor(
        db, 
        approval.vendor_id, 
        current_employee.employee_id
    )
    if not approved_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return approved_vendor

@router.get("/me", response_model=VendorPublic)
def get_my_profile(
    current_vendor: CurrentVendor  # Only vendors can access
):
    return current_vendor

@router.patch("/me", response_model=VendorPublic)
def update_my_profile(
    updates: VendorProfileUpdate,
    current_vendor: CurrentVendor,  # Only vendors can access
    db: Session = Depends(get_db),
):
    updated_vendor = vendor_service.update_vendor_profile(
        db, 
        current_vendor.vendor_id, 
        updates
    )
    if not updated_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return updated_vendor