from datetime import datetime
from enum import Enum
from typing import Optional, List
from shared.models.base import BaseModelWithConfig
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"


class OrderItem(BaseModelWithConfig):
    product_id: str
    quantity: int = Field(gt=0)
    price_per_unit: float = Field(gt=0)


class OrderBase(BaseModel):
    user_id: str
    items: List[OrderItem]
    shipping_address: str


class OrderCreate(BaseModel):
    items: List[OrderItem]
    shipping_address: str


class OrderUpdate(BaseModelWithConfig):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None


class OrderResponse(OrderBase):
    id: str
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime
