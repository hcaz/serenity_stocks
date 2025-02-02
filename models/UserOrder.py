from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class UserOrder(BaseModel):
    id: Optional[str] = None
    email: str
    symbol: str
    category: str
    quantity: int
    price: Optional[int] = None
    created_at: Optional[float] = None
    completed_at: Optional[float] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
