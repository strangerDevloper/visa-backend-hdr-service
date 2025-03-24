# app/api/user/user_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query  # Import Query here!
from sqlalchemy.orm import Session

from app.core.constants import USER_TYPE_USER
from ...config.database import get_db
from . import user_types, user_service
from ...helpers import auth_utils
from fastapi.security import OAuth2PasswordRequestForm
from ...api.dependencies import CurrentUser
from typing import List, Dict, Union, Any

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=user_types.User, status_code=status.HTTP_201_CREATED)
def signup(user: user_types.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.create_user(db, user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Username already registered")
    return db_user

@router.post("/signin", response_model=user_types.Token)
def signin_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_username(db, form_data.username)
    if not db_user or not auth_utils.verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    user_id = db_user.user_id
    user_type = USER_TYPE_USER

    access_token = auth_utils.create_access_token(data={"sub": str(user_id)}, user_type=user_type)
    user_service.update_login_info(db, db_user.user_id)
    return user_types.Token(access_token=access_token)

@router.get("/", response_model=Dict[str, Union[List[user_types.User], int]])
def get_all_users(
    current_user: CurrentUser,
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(10, description="Number of items to retrieve"),
    db: Session = Depends(get_db),
):
    """Lists all active users with pagination and returns total count."""
    users, total_count = user_service.get_active_users_paginated(db, skip=skip, limit=limit)
    return {"users": users, "total_count": total_count}

@router.get("/{user_id}", response_model=user_types.User)
def get_user_by_id(user_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Gets a specific user by ID."""
    db_user = user_service.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=user_types.User)
def update_user(
    user_id: int,
    user_update: user_types.UserUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Updates a specific user."""
    updated_user = user_service.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Deactivates a specific user."""
    user_service.deactivate_user(db, user_id)
    return