from typing import Optional, Any
from pydantic import BaseModel, field_serializer
from enum import Enum


class OrderTypeEnum(Enum):
    SHARE = "SHARE"
    SHORT = "SHORT"

class UserOrder(BaseModel):
    email: str
    symbol: str
    category: str
    type: OrderTypeEnum
    quantity: int
    price: Optional[int] = None
    created_at: Optional[float] = None
    completed_at: Optional[float] = None

    @field_serializer('type')
    def serialize_order_type(self, order_type: OrderTypeEnum) -> str:
        return order_type.value