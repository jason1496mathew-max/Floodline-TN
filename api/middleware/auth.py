"""
JWT Authentication Middleware for FastAPI
==========================================

Handles JWT token creation and verification for protected endpoints.

Features:
    - JWT token generation
    - Token verification and validation
    - Mock login system for demo
    - Configurable expiration

Usage:
    from api.middleware.auth import verify_token
    
    @router.post("/protected")
    async def protected_route(credentials: HTTPAuthorizationCredentials = Depends(security)):
        payload = verify_token(credentials.credentials)
        # Your logic here
"""

from fastapi import HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os


# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "floodline-tn-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing token payload (must include 'sub' for subject)
    
    Returns:
        Encoded JWT token string
    
    Example:
        >>> token = create_access_token({"sub": "admin"})
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary containing token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    
    Example:
        >>> payload = verify_token("eyJhbGciOiJIUzI1NiIs...")
        >>> username = payload["sub"]
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


def login_for_access_token(username: str, password: str) -> dict:
    """
    Mock login - in production, verify against database
    
    Args:
        username: Username
        password: Password
    
    Returns:
        Dictionary with access_token and token_type
    
    Raises:
        HTTPException: If credentials are incorrect
    
    Example:
        >>> token_data = login_for_access_token("admin", "floodline2024")
        >>> print(token_data["access_token"])
    """
    # Hardcoded demo credentials (replace with database check in production)
    if username == "admin" and password == "floodline2024":
        access_token = create_access_token(data={"sub": username})
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
