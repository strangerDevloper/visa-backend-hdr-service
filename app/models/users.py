# app/models/users.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from ..config.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    contact_no = Column(String)
    active_status = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    created_on = Column(DateTime, server_default=func.now())
    changed_on = Column(DateTime, server_default=func.now(), onupdate=func.now())