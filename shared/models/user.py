from pydantic import EmailStr
from shared.models.base import BaseModelWithConfig, TimestampedModel
from datetime import datetime


class UserBase(BaseModelWithConfig):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase, TimestampedModel):
    id: str
    hashed_password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
