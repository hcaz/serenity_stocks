import json
import math
import random
import time
from fastapi import HTTPException
from pymongo import UpdateOne, DESCENDING
from models.Stock import StockInstance
from AtlasClient import getClient
from models.UserStock import UserStock

stock_instances_collection = getClient().get_collection("serenity_stocks", "stock_instances")
user_stocks_collection = getClient().get_collection("serenity_stocks", "user_stocks")

def get_stocks() -> list[StockInstance]:
    """
    Fetch a list of stock documents.
    """
    stocks = []
    cursor = stock_instances_collection.find({}).sort("date", DESCENDING).limit(1000)
    cursor = list(cursor)
    for document in cursor:
        stocks.append(StockInstance(**document))
    return stocks

def get_user_stocks(email: str):
    """
    Fetch a list of stock documents.
    """
    stocks = []
    cursor = user_stocks_collection.find({
        "email": email,
    })
    cursor = list(cursor)
    for document in cursor:
        stocks.append(UserStock(**document))
    return stocks


def get_stock(symbol: str):
    """
    Fetch a single stock document by symbol.
    """
    stock = stock_instances_collection.find_one({"symbol": symbol}).sort("date", DESCENDING).limit(50)
    if stock:
        return StockInstance(**stock)
    raise HTTPException(status_code=404, detail="Stock not found")


def add_stock(stock: StockInstance):
    """
    Add a new stock document.
    """
    # Here you would typically fetch the current price, daily increase,
    # and chart data from an external API or data source
    # For this example, we'll just use the data provided in the request body
    stock_dict = stock.dict()
    stock_dict["date_added"] = time.time()
    result = stock_instances_collection.insert_one(stock_dict)
    return StockInstance(**stock_dict)

def reset_stocks():
    stock_instances_collection.delete_many({})

    myStocks = []
    with open("stocks.json", "r") as json_file:
        stock_data = json.load(json_file)
        for stock_json in stock_data:
            myStocks.append(StockInstance(
                name = stock_json['name'], 
                symbol = stock_json['symbol'], 
                category = stock_json['category'],
                max_shares = stock_json['max_shares'],
                available_shares = stock_json['available_shares'],
                date = stock_json['historic_data'][0]['date'], 
                price = stock_json['historic_data'][0]['price'],
            ).dict())

    stock_instances_collection.insert_many(myStocks)
    return

def tick_stocks():
    timestamp = time.time()
    all_stocks = get_stocks()
    all_latest_stocks = {}
    for stock in all_stocks:
        if stock.symbol in all_latest_stocks:
            continue
        all_latest_stocks[stock.symbol] = stock
    all_stocks = list(all_latest_stocks.values())

    if math.ceil(timestamp) < all_stocks[0].date:
        return

    newStocks = []
    for stock in all_stocks:
        # base level flux
        baseFlux = random.uniform(-0.01, 0.01)

        # category news flux

        # stock news flux

        # user actions flux

        newStocks.append(StockInstance(
            name = stock.name, 
            symbol = stock.symbol, 
            category = stock.category,
            max_shares = stock.max_shares,
            available_shares = stock.available_shares,
            date = timestamp,
            price = int(stock.historic_data[-1].price * (1 + baseFlux)),
        ).dict())
    stock_instances_collection.insert_many(newStocks)
    return

def burst_the_bubble():
    """Tanks the entire stock market by drastically reducing prices."""

    all_stocks = get_stocks()
    all_latest_stocks = {}
    for stock in all_stocks:
        if stock.symbol in all_latest_stocks:
            continue
        all_latest_stocks[stock.symbol] = stock
    all_stocks = list(all_latest_stocks.values())
    
    for stock in all_stocks:
        current_price = stock.price
        
        new_price = current_price * random.uniform(0.2, 0.5)

        # Update the stock in the database
        stock_instances_collection.insert_one(StockInstance(
            name = stock.name, 
            symbol = stock.symbol, 
            category = stock.category,
            max_shares = stock.max_shares,
            available_shares = stock.available_shares,
            date = time.time(),
            price = round(new_price),
        ).dict())