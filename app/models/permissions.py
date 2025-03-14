# app/models/permissions.py
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from ..database import Base

class MethodEnum(PyEnum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'

class ActionEnum(PyEnum):
    CREATE = 'CREATE'
    READ = 'READ'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

class Permissions(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True, autoincrement=True)
    permission_name = Column(String)
    description = Column(Text, nullable=True)
    resource = Column(String)
    action = Column(Enum(ActionEnum))
    method = Column(Enum(MethodEnum))

    # Optional: Relationship to a table that uses permissions (e.g., roles_permissions)
    # roles_permissions = relationship("RolesPermissions", back_populates="permission")