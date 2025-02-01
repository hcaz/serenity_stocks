import time
import uuid

from fastapi import HTTPException
from pymongo import UpdateOne
from AtlasClient import getClient
from Stock import DataNode, Stock
from UserOrder import UserOrder
from UserStock import UserStock

orders_collection = getClient().get_collection("serenity_stocks", "user_orders")
user_stocks_collection = getClient().get_collection("serenity_stocks", "user_stocks")
stocks_collection = getClient().get_collection("serenity_stocks", "stocks")
user_collection = getClient().get_collection("serenity_stocks", "users")

def get_open_orders(email: str):
    existing_user = user_collection.find_one({"email": email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

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
    existing_user = user_collection.find_one({"email": order.email})
    existing_stock = stocks_collection.find_one({"symbol": order.symbol})
    if not existing_user :
        raise HTTPException(status_code=404, detail="User not found")
    if not existing_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    order_dict = order.dict()
    order_dict["id"] = str(uuid.uuid4())
    order_dict["created_at"] = time.time()
    result = orders_collection.insert_one(order_dict)
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

    user_stocks = user_stocks_collection.find({
        "email": {
            "$in": [o.email for o in all_open_orders]
        },
    })
    user_stocks = list(user_stocks)
    user_stocks = [UserStock(**document) for document in user_stocks]

    for order in all_open_orders:
        # first stock in all stocks where stock.symbol == order.symbol
        stock_index = next((index for index, stock in enumerate(all_stocks) if stock.symbol == order.symbol), None) 
        if stock_index is None:
            continue
        stock = all_stocks[stock_index]
        if stock.available_shares < order.quantity:
            orders_collection.delete_one({"id": order.id})
            continue
        stock.available_shares = stock.available_shares - order.quantity
        order.price = stock.historic_data[-1].price
        order.completed_at = time.time()

        targetUserStock = next((userStock for userStock in user_stocks if userStock.symbol == order.symbol and userStock.email == order.email), None)
        if targetUserStock is None:
            targetUserStock = UserStock(
                email = order.email,
                symbol = order.symbol,
                category = order.category,
                quantity = 0,
                purchase_log=[],
            )
        
        targetUserStock.quantity = targetUserStock.quantity + order.quantity
        targetUserStock.purchase_log.append(order)
        targetUserStock.updated_at = time.time()
        filter_query = {
            "symbol": order.symbol,
            "email": order.email,
        }

        user_stocks_collection.update_one(filter_query, {"$set":targetUserStock.dict()}, upsert=True)

        orders_collection.replace_one({"id": order.id}, order.dict())

        newPrice = calculate_updated_price(stock, order)
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

    order_impact = (order.quantity / stock.available_shares) * pressure if stock.available_shares > 0 else 0

    updated_price = current_price + (current_price * order_impact * volatility_factor)
    return round(updated_price)  # Round to the nearest integer
