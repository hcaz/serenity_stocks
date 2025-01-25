from pydantic import BaseModel

# Pydantic model for stock data

class DataNode(BaseModel):
    date: int
    price: int

class Stock(BaseModel):
    name: str
    symbol: str
    category: str
    max_shares: int
    available_shares: int
    historic_data: list[DataNode]