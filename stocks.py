from fastapi import HTTPException
from Stock import Stock
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
    for document in cursor:  # Limit to 100 documents for now
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