from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import dotenv_values
import datetime

# Load environment variables (including MongoDB Atlas connection string)
config = dotenv_values(".env")
ATLAS_URI = config["ATLAS_URI"]

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # Adjust origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for stock data
class Stock(BaseModel):
    symbol: str
    current_price: float
    daily_increase: float
    day_data: list[float]
    week_data: list[float]
    month_data: list[float]


# MongoDB Atlas client
class AtlasClient:
    client: MongoClient

    def __init__(self, uri: str):
        self.client = MongoClient(uri)

    def get_collection(self, database_name: str, collection_name: str):
        return self.client[database_name][collection_name]


# Initialize the MongoDB Atlas client
app.mongodb_client = AtlasClient(ATLAS_URI)
stock_collection = app.mongodb_client.get_collection("stock_database", "stocks")  # Replace with your database and collection names


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.client.close()


@app.get("/stocks/", response_model=list[Stock])
async def get_stocks():
    """
    Fetch a list of stock documents.
    """
    stocks = []
    cursor = stock_collection.find({})  # Fetch all documents
    for document in await cursor.to_list(length=100):  # Limit to 100 documents for now
        stocks.append(Stock(**document))
    return stocks


@app.get("/stocks/{symbol}", response_model=Stock)
async def get_stock(symbol: str):
    """
    Fetch a single stock document by symbol.
    """
    stock = await stock_collection.find_one({"symbol": symbol})
    if stock:
        return Stock(**stock)
    raise HTTPException(status_code=404, detail="Stock not found")


@app.post("/stocks/", response_model=Stock)
async def add_stock(stock: Stock):
    """
    Add a new stock document.
    """
    # Here you would typically fetch the current price, daily increase,
    # and chart data from an external API or data source
    # For this example, we'll just use the data provided in the request body
    stock_dict = stock.dict()
    stock_dict["date_added"] = datetime.datetime.now()
    result = await stock_collection.insert_one(stock_dict)
    return Stock(**stock_dict)