from typing import Optional, Any
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer

class UserOrder(BaseModel):
    # id: ObjectId = Field(alias="_id", default=None) 
    email: str
    symbol: str
    category: str
    quantity: int
    price: Optional[int] = None
    created_at: Optional[float] = None
    completed_at: Optional[float] = None

    # model_config = ConfigDict(
    #     arbitrary_types_allowed=True,
    #     exclude={id}
    # )

    # def dict(self, *args, **kwargs):
    #     kwargs['exclude'] = {'id'}
    #     return super().dict(*args, **kwargs)