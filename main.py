from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import dotenv_values

from Stock import Stock
from User import User
from users import login, profile

from stocks import get_stock, get_stocks, reset_stocks, tick_stocks

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

#User endpoints
@app.get("/login/{email}", response_model=User)
def add_login_endpoint(email: str): 
    return login(email) 

@app.get("/profile/{email}", response_model=User)
def get_profile_endpoint(email: str):
    return profile(email)

#Stock endpoints
@app.get("/stocks/", response_model=list[Stock])
def get_stocks_endpoint():
    return get_stocks()


@app.get("/stock/{symbol}", response_model=Stock)
def get_stock_endpoint(symbol: str):
    return get_stock(symbol)

@app.post("/stocks/reset")
def reset_all_stocks_endpoint(stock: Stock): 
    return reset_stocks() 

@app.post("/stocks/tick")
def tick_all_stocks_endpoint(stock: Stock): 
    return tick_stocks() 
