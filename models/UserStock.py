from typing import Optional, Any
from pydantic import BaseModel
from models.UserOrder import UserOrder

class UserStock(BaseModel):
    email: str
    symbol: str
    category: str
    quantity: int
    purchase_log: list[UserOrder]
    updated_at: Optional[float] = None