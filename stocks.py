import json
import math
import random
import time
from fastapi import HTTPException
from pymongo import UpdateOne
from Stock import DataNode, Stock
from AtlasClient import getClient

stock_collection = getClient().get_collection("serenity_stocks", "stocks")

def get_stocks():
    """
    Fetch a list of stock documents.
    """
    stocks = []
    cursor = stock_collection.find({})  # Fetch all documents
    cursor = list(cursor)
    for document in cursor:
        stocks.append(Stock(**document))
    return stocks


def get_stock(symbol: str):
    """
    Fetch a single stock document by symbol.
    """
    stock = stock_collection.find_one({"symbol": symbol})
    if stock:
        return Stock(**stock)
    raise HTTPException(status_code=404, detail="Stock not found")


def add_stock(stock: Stock):
    """
    Add a new stock document.
    """
    # Here you would typically fetch the current price, daily increase,
    # and chart data from an external API or data source
    # For this example, we'll just use the data provided in the request body
    stock_dict = stock.dict()
    stock_dict["date_added"] = time.time()
    result = stock_collection.insert_one(stock_dict)
    print(result)
    return Stock(**stock_dict)

def reset_stocks():
    stock_collection.delete_many({})

    myStocks = []
    with open("stocks.json", "r") as json_file:
        stock_data = json.load(json_file)
        for stock_json in stock_data:
            historic_data = []
            for data_node_json in stock_json['historic_data']:
                data_node = DataNode(
                    date = data_node_json['date'], 
                    price = data_node_json['price'],
                )
                historic_data.append(data_node)
            stock = Stock(
                name = stock_json['name'], 
                symbol = stock_json['symbol'], 
                category = stock_json['category'],
                max_shares = stock_json['max_shares'],
                available_shares = stock_json['available_shares'],
                historic_data = historic_data,
            )
            myStocks.append(stock.dict())

    stock_collection.insert_many(myStocks)
    return

def tick_stocks():
    timestamp = time.time()
    print(timestamp)
    all_stocks = get_stocks()
    if math.ceil(timestamp) < all_stocks[0].historic_data[-1].date:
        return

    operations = []
    for stock in all_stocks:
        # base level flux
        baseFlux = random.uniform(-0.01, 0.01)

        # category news flux

        # stock news flux

        # user flux

        # order influence
        stock.historic_data.append(
            DataNode(
                date = timestamp,
                price = int(stock.historic_data[-1].price * (1 + baseFlux)),
            )
        )
        newData = [data.dict() for data in stock.historic_data]
        operations.append(
            UpdateOne(
                {"symbol": stock.symbol},  # Filter by stock symbol
                {"$set": {"historic_data": newData}}  # Update historic_data
            )
        )
    stock_collection.bulk_write(operations)
    return