from pydantic import BaseModel
from typing import Optional

# Pydantic model for user data
class User(BaseModel):
    email: str
    name: str
    job_role: str
    last_seen: Optional[float] = None
    balance: float
    budget_remaining: float
    joined: float

    tone: Optional[str] = None
    aggression_level: Optional[int] = None
    personality_prompt: Optional[str] = None