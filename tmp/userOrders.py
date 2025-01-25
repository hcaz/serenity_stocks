import time

from pymongo import UpdateOne
from AtlasClient import getClient
from Stock import DataNode, Stock
from UserOrder import UserOrder

orders_collection = getClient().get_collection("serenity_stocks", "user_orders")
stocks_collection = getClient().get_collection("serenity_stocks", "stocks")

def get_open_orders(email: str):
    orders = []
    cursor = orders_collection.find({
        "email": email,
        "completed_at": None,
    })
    cursor = list(cursor)
    for document in cursor:
        orders.append(UserOrder(**document))
    return orders

def add_order(order: UserOrder):
    order_dict = order.dict()
    order_dict["created_at"] = time.time()
    result = orders_collection.insert_one(order_dict)
    print(result)
    return UserOrder(**order_dict)

def compute_open_orders():
    all_open_orders = orders_collection.find({
        "completed_at": None,
    })
    all_open_orders = list(all_open_orders)
    all_open_orders = [UserOrder(**document) for document in all_open_orders]
    all_stocks = stocks_collection.find({})
    all_stocks = list(all_stocks)
    all_stocks = [Stock(**document) for document in all_stocks]

    for order in all_open_orders:
        # first stock in all stocks where stock.symbol == order.symbol
        stock_index = next((index for index, stock in enumerate(all_stocks) if stock.symbol == order.symbol), None) 
        if stock_index is None:
            continue
        stock = all_stocks[stock_index]
        stock.available_shares = stock.available_shares - order.quantity
        order.price = stock.historic_data[-1].price
        order.completed_at = time.time()
        orders_collection.replace_one({"symbol": order.symbol}, order.dict())

        newPrice = calculate_updated_price(stock, order)
        print(newPrice)
        print(order.price)
        stock.historic_data.append(
            DataNode(
                date = time.time(),
                price = newPrice,
            )
        )

    operations = []
    for stock in all_stocks:
        operations.append(
            UpdateOne(
                {"symbol": stock.symbol},  # Filter by stock symbol
                {"$set": {
                    "historic_data": [data.dict() for data in stock.historic_data],
                    "available_shares": stock.available_shares,
                }}
            )
        )
    stocks_collection.bulk_write(operations)



def calculate_updated_price(stock: Stock, order: UserOrder) -> int:
    """Calculates the updated price of a stock based on a user order."""

    current_price = stock.historic_data[-1].price  # Get the latest price
    volatility_factor = 2  # A value representing the stock's volatility (e.g., a value between 0.1 for low volatility and 0.5 for high volatility)
    pressure = 1.2 # A multiplier to adjust the impact of buy orders
    if order.quantity < 0:
        pressure = -1.0 # A multiplier to adjust the impact of sell orders

    order_impact = (order.quantity / stock.available_shares) * pressure

    updated_price = current_price + (current_price * order_impact * volatility_factor)
    return round(updated_price)  # Round to the nearest integer
