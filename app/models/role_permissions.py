# app/models/role_permissions.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base

class RolePermissions(Base):
    __tablename__ = "role_permissions"

    role_permission_id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('role_hdr.role_id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.permission_id'), nullable=False)
    granted_at = Column(DateTime, server_default=func.now())

    role = relationship("RoleHdr", backref="role_permissions")
    permission = relationship("Permissions", backref="role_permissions")