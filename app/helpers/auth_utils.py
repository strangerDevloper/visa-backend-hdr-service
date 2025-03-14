# app/helpers/auth_utils.py
import secrets
import string
from passlib.context import CryptContext # type: ignore
from datetime import datetime, timedelta
from typing import Dict, Tuple
from jose import jwt # type: ignore
import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def generate_random_password(length=8):
    """Generates a random password with only alphanumeric characters."""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None, user_type: str = "employee") -> str:
    """Creates a JWT access token with user type."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "user_type": user_type})  # Add user type
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict:
    """Decodes a JWT access token and returns payload with user type."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

def extract_user_data(token: str) -> Tuple[int, str] | None:
    """Extracts user ID and type from a JWT token."""
    payload = decode_access_token(token)
    if payload:
        user_id = int(payload.get("sub"))
        user_type = payload.get("user_type")
        return user_id, user_type
    return None