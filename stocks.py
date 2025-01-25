import json
from fastapi import HTTPException
from Stock import DataNode, Stock
from AtlasClient import getClient

import datetime

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
    stock_dict["date_added"] = datetime.datetime.now()
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
                historic_data = historic_data,
            )
            myStocks.append(stock.dict())

    stock_collection.insert_many(myStocks)
    return