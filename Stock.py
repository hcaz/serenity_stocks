from pydantic import BaseModel

# Pydantic model for stock data
class Stock(BaseModel):
    symbol: str
    current_price: float
    daily_increase: float
    day_data: list[float]
    week_data: list[float]
    month_data: list[float]