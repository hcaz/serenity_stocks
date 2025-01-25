from pydantic import BaseModel

class News(BaseModel):
    title: str
    body: str
    publisher: str
    positivity: int # 1 - 5
    affected_stocks: list[str]
    affected_categories: list[str]
    timestamp: float
    