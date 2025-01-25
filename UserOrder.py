from typing import Optional
from pydantic import BaseModel

class UserOrder(BaseModel):
    email: str
    symbol: str
    category: str
    quantity: int
    price: Optional[int] = None
    created_at: Optional[float] = None
    completed_at: Optional[float] = None