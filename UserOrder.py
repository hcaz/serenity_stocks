from typing import Optional, Any
from pydantic import BaseModel, field_serializer
from enum import Enum

class UserOrder(BaseModel):
    email: str
    symbol: str
    category: str
    quantity: int
    price: Optional[int] = None
    created_at: Optional[float] = None
    completed_at: Optional[float] = None
