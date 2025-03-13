# app/api/user/user.types.py
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    name: str
    username: str
    email: str
    contact_no: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    contact_no: str | None = None
    password: str | None = None

class User(UserBase):
    user_id: int
    active_status: bool
    last_login: datetime | None = None
    login_count: int
    created_on: datetime
    changed_on: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"