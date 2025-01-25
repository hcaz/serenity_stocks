from pydantic import BaseModel
from enum import Enum

# Pydantic model for user data
class User(BaseModel):
    email: str
    name: str
    job_role: str
    last_seen: float
    balance: float
    budget_remaining: float
    joined: float