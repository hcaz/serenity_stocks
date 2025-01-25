from pydantic import BaseModel

class JobRole(BaseModel):
    name: str
    code: str
    daily_budget: int