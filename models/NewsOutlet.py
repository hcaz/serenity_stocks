from pydantic import BaseModel

class NewsOutlet(BaseModel):
    name: str
    tone: str
    style: str
    bias: str
    positive_stocks: list[str] = []
    negative_stocks: list[str] = []
    positive_categories: list[str] = []
    negative_categories: list[str] = []
