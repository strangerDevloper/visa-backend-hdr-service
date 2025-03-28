from typing import Literal
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.api.common.common_service import get_employee_response, get_user_response, get_vendor_response
from app.api.employee import employee_service
from app.api.user import user_service
from app.helpers import auth_utils
from app.models.employees import EmployeeHdr
from app.models.users import User
from app.models.vendor import Vendor
from ...config.database import get_db
from ..dependencies import CurrentUser,CurrentEmployee
from app.api.common.common_types import  SignInRequest, Token, UserOrEmployeeResponse
from app.core.constants import USER_TYPE_EMPLOYEE, USER_TYPE_USER, UserType



router = APIRouter()

router = APIRouter(prefix="/api", tags=["common"])

@router.get("/me", response_model=UserOrEmployeeResponse)
async def get_current_user_details(current_user: CurrentUser, db: Session = Depends(get_db)):
    """
    Returns the details of the currently logged-in user.
    """
    if isinstance(current_user, User):
        return get_user_response(current_user)
    elif isinstance(current_user, EmployeeHdr):
        return get_employee_response(current_user, db)
    elif isinstance(current_user, Vendor):
        return get_vendor_response(current_user)
    else:
        raise HTTPException(status_code=400, detail="Invalid user type.")
    

@router.post("/signin", response_model=Token)
def common_signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Common sign-in endpoint for both users and employees.
    The `user_type` parameter specifies whether the user is signing in as a "user" or "employee".
    """
    user_type = None
    if form_data.grant_type == UserType.USER:
        # Authenticate as a user
        user_type = USER_TYPE_USER
        db_user = user_service.get_user_by_username(db, form_data.username)
        if not db_user or not auth_utils.verify_password(form_data.password, db_user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        user_id = db_user.user_id
        user_service.update_login_info(db, db_user.user_id)
    # elif form_data.grant_type == UserType.EMPLOYEE:
    else:
        # Authenticate as an employee
        user_type = USER_TYPE_EMPLOYEE
        db_employee = employee_service.get_employee_by_email(db, form_data.username)
        if not db_employee or not auth_utils.verify_password(form_data.password, db_employee.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        user_id = db_employee.employee_id
        employee_service.update_login_info(db, db_employee.employee_id)
    # else:
    #     raise HTTPException(status_code=400, detail="Invalid user type")

    # Generate a token
    access_token = auth_utils.create_access_token(data={"sub": str(user_id)}, user_type=user_type)
    return Token(access_token=access_token)