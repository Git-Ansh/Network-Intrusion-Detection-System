# backend/auth_simple.py - Simplified auth without bcrypt issues

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import hashlib

# --- Configuration and Setup ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-for-development-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# OAuth2 scheme that specifies the token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a router to group authentication-related endpoints
router = APIRouter()

# Simple password hashing (for demo only - use bcrypt in production)
def simple_hash(password: str) -> str:
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_simple_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against simple hash"""
    return simple_hash(plain_password) == hashed_password

# --- In-Memory User Database (for prototype) ---
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": simple_hash("testpassword"),
        "disabled": False,
    }
}

from typing import Optional

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency for Protected Routes ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decodes the JWT token to get the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = fake_users_db.get(username)
    if user is None or user.get("disabled"):
        raise credentials_exception
    return user

# --- API Endpoints for Authentication ---
@router.post("/token", summary="User Login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns an access token.
    """
    user = fake_users_db.get(form_data.username)
    if not user or not verify_simple_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", summary="Get Current User Info")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    A protected endpoint to get information about the currently logged-in user.
    """
    return {"username": current_user["username"], "full_name": current_user["full_name"]}
