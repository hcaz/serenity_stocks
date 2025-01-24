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
    amazon = Stock(
        name="Amazon",
        symbol="AMZN",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )
    yahoo = Stock(
        name="Yahoo",
        symbol="YHOO",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )
    ebay = Stock(
        name="eBay",
        symbol="EBAY",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )
    myspace = Stock(
        name="MySpace",
        symbol="MSP",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )
    petscom = Stock(
        name="pets.com",
        symbol="PCOM",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )
    cisco = Stock(
        name="Cisco",
        symbol="CSCO",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )
    microsoft = Stock(
        name="Microsoft",
        symbol="MSFT",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )
    apple = Stock(
        name="Apple",
        symbol="AAPL",
        historic_data=[
            DataNode(
                date=0,
                price=26800
            )
        ]
    )

    stock_collection.insert_many([
        amazon.dict(),
        yahoo.dict(),
        ebay.dict(),
        myspace.dict(),
        petscom.dict(),
        cisco.dict(),
        microsoft.dict(),
        apple.dict()
    ])
    return