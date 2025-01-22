"""
Authentication and authorization utilities.
Handles password hashing, JWT token generation, and verification.
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from shared.models.base import TokenData
from database import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Middleware dependency for authenticating requests.
    Verifies JWT token and returns the current user.
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        email = payload.get("sub")
        user_id = payload.get("user_id")

        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        token_data = TokenData(email=email, user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    database = await db.get_database()
    user = await database.users.find_one({"email": token_data.email})

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
