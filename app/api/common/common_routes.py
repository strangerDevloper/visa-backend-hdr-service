from fastapi import APIRouter, Depends
from typing import Union
from ..dependencies import CurrentUser
from ...models import User, EmployeeHdr
from app.api.common.common_types import UserOrEmployeeResponse, UserResponse, EmployeeResponse


router = APIRouter()

# router = APIRouter(prefix="/api", tags=["common"])


# @router.get("/me", response_model=Union[User, EmployeeHdr])
# async def get_current_user_details(current_user: CurrentUser):
#     """
#     Returns the details of the currently logged-in user.
#     """
#     return current_user


# @router.get("/me", response_model=UserOrEmployeeResponse)
# async def get_current_user_details(current_user: CurrentUser):
#     """
#     Returns the details of the currently logged-in user.
#     """
#     if isinstance(current_user, User):
#         return UserResponse(
#             user_type="USER",
#             user_id=current_user.user_id,
#             username=current_user.username,
#             email=current_user.email,
#         )
#     elif isinstance(current_user, EmployeeHdr):
#         return EmployeeResponse(
#             user_type="EMPLOYEE",
#             employee_id=current_user.employee_id,
#             employee_name=current_user.employee_name,
#             email=current_user.email,
#         )
#     else:
#         raise HTTPException(status_code=400, detail="Invalid user type.")