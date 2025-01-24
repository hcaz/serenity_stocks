from pydantic import BaseModel

# Pydantic model for stock data

class DataNode(BaseModel):
    date: int
    price: int

class Stock(BaseModel):
    name: str
    symbol: str
    historic_data: list[DataNode]