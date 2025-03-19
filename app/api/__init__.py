# app/api/__init__.py
from .user import router as users_router
from .employee import router as employee_router #Add employee router
from .country import router as country_router #Add country router
from .common import router as common_router #Add common router
from .role import router as role_router #Add role router