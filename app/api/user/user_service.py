# app/api/user/user.service.py
from sqlalchemy.orm import Session
from ... import models
from ...helpers import auth_utils
from . import user_types
from datetime import datetime

def create_user(db: Session, user: user_types.UserCreate):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        return None
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        contact_no=user.contact_no,
        password_hash=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def update_user(db: Session, user_id: int, user_update: user_types.UserUpdate):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user:
        for key, value in user_update.dict(exclude_unset=True).items():
            if key == "password":
                setattr(db_user, "password_hash", auth_utils.get_password_hash(value))
            else:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user:
        db_user.active_status = False
        db_user.changed_on = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user

def update_login_info(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user:
      db_user.last_login = datetime.utcnow()
      db_user.login_count += 1
      db.commit()
      db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    """Retrieves a user by their ID."""
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_all_users(db: Session):
    """Retrieves all users."""
    return db.query(models.User).all()

def get_active_users_paginated(db: Session, skip: int = 0, limit: int = 10):
    """Retrieves active users with pagination and returns total count."""
    query = db.query(models.User).filter(models.User.active_status == True)
    total_count = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total_count
