# app/api/user/user_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database import get_db
from . import user_types, user_service
from ...helpers import auth_utils
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/signin")

@router.post("/signup", response_model=user_types.User, status_code=status.HTTP_201_CREATED)
def signup(user: user_types.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.create_user(db, user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Username already registered")
    return db_user

@router.post("/signin", response_model=user_types.Token)
def signin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_username(db, form_data.username)
    if not db_user or not auth_utils.verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth_utils.create_access_token(data={"sub": str(db_user.user_id)})
    user_service.update_login_info(db, db_user.user_id)
    return user_types.Token(access_token=access_token)

@router.put("/{user_id}", response_model=user_types.User)
def update_user(user_id: int, user_update: user_types.UserUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Add authentication logic here if needed
    updated_user = user_service.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Add authentication logic here if needed
    user_service.deactivate_user(db, user_id)