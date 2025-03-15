# app/api/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from ..helpers import auth_utils
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Annotated, Callable, Union
from .. import models
from fastapi.security import OAuth2PasswordBearer
from ..core import constants

employee_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/employees/signin")
user_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/signin")

def get_user_from_token(token: str):
    """Extracts user ID and type from token."""
    user_data = auth_utils.extract_user_data(token)
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user_data

def authorize_user_type(request: Request, user_type_from_token: tuple[int, str]):
    """Authorizes access based on user type and route prefix."""
    _, user_type = user_type_from_token
    allowed_routes = constants.ACCESS_RULES.get(user_type, [])
    path_allowed = False
    for allowed_prefix in allowed_routes:
        if request.url.path.startswith(allowed_prefix):
            path_allowed = True
            break

    if not path_allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access based on user type.")

def get_current_employee(request: Request, token: str = Depends(employee_oauth2_scheme), db: Session = Depends(get_db)):
    """Decorator to get the current employee based on the token."""
    user_id, user_type = get_user_from_token(token)
    authorize_user_type(request, (user_id, user_type))

    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == user_id).first()
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return db_employee

def get_current_user(request: Request, token: str = Depends(user_oauth2_scheme), db: Session = Depends(get_db)):
    """Decorator to get the current user based on the token."""
    user_id, user_type = get_user_from_token(token)
    authorize_user_type(request, (user_id, user_type))

    if user_type == constants.USER_TYPE_USER:
        db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return db_user
    elif user_type == constants.USER_TYPE_EMPLOYEE:
        db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == user_id).first()
        if not db_employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return db_employee
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user type in token.")


CurrentUser = Annotated[Union[models.EmployeeHdr, models.User], Depends(get_current_user)]
CurrentEmployee = Annotated[models.EmployeeHdr, Depends(get_current_employee)]