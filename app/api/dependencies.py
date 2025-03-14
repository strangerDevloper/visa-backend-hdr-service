# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from ..helpers import auth_utils
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Annotated, Callable
from .. import models
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/employees/signin")

def get_current_user(model: Callable, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Decorator to get the current user based on the token and user type."""
    user_data = auth_utils.extract_user_data(token)
    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id, user_type = user_data

    db_user = db.query(model).filter(model.employee_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user

CurrentEmployee = Annotated[models.EmployeeHdr, Depends(lambda token=Depends(oauth2_scheme), db=Depends(get_db): get_current_user(models.EmployeeHdr, token, db))]