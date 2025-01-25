from typing import Optional
from pydantic import BaseModel
from bson import ObjectId

class UserOrder(BaseModel):
    userId: ObjectId
    symbol: str
    category: str
    quantity: int
    price: Optional[int] = None
    created_at: float
    completed_at: Optional[float] = None