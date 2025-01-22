from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class BaseModelWithConfig(BaseModel):
    class Config:
        from_attributes = True
        exclude_unset = True


class TimestampedModel(BaseModelWithConfig):
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
