from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import dotenv_values

from Stock import Stock
from stocks import add_stock, get_stock, get_stocks, reset_stocks

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

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.client.close()


@app.get("/stocks/", response_model=list[Stock])
def get_stocks_endpoint():
    return get_stocks()


@app.get("/stocks/{symbol}", response_model=Stock)
def get_stock_endpoint(symbol: str):
    return get_stock(symbol)


@app.post("/stocks/", response_model=Stock)
def add_stock_endpoint(stock: Stock): 
    return add_stock(stock) 

@app.post("/stocks/reset")
def reset_all_stocks_endpoint(stock: Stock): 
    return reset_stocks() 
