from typing import Optional, Any
from pydantic import BaseModel, field_serializer
from UserOrder import UserOrder

class UserStock(BaseModel):
    email: str
    symbol: str
    category: str
    quantity: int
    purchase_log: list[UserOrder]
    updated_at: Optional[float] = None