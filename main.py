from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import dotenv_values
from bson import ObjectId

from News import News
from Stock import Stock
from User import User
from UserOrder import UserOrder
from newsGenerator import generate_random_article, reset_news
from scheduler import scheduler
from userOrders import add_order, get_open_orders
from users import login, profile, reset_users

from stocks import burst_the_bubble, get_stock, get_stocks, reset_stocks, tick_stocks
from Notification import Notification
from notifications import get_notifications, read_notification
from stocks import get_stock, get_stocks, reset_stocks
from stocks import get_stock, get_stocks, reset_stocks, tick_stocks
from Notification import Notification, NotificationReply
from notifications import get_notifications, read_notification, reply_to_notification, create_notification
from stocks import add_stock, get_stock, get_stocks, reset_stocks

# Load environment variables (including MongoDB Atlas connection string)
config = dotenv_values(".env")
ATLAS_URI = config["ATLAS_URI"]
GEMINI_API_KEY = config["GEMINI_API_KEY"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

#User endpoints
@app.get("/login/{email}", response_model=User)
def add_login_endpoint(email: str): 
    return login(email) 

@app.get("/profile/{email}", response_model=User)
def get_profile_endpoint(email: str):
    return profile(email)

@app.post("/users/reset")
def reset_all_users_endpoint(): 
    return reset_users() 

@app.post("/notification/{sender}/{recipient}", response_model=Notification)
def create_notifications_endpoint(sender: str, recipient: str, subject: str, message: str):
    return create_notification(sender, recipient, subject, message)

@app.get("/notifications/{email}", response_model=list[Notification])
def get_notifications_endpoint(email: str):
    return get_notifications(email)

@app.get("/notification/{id}/read", response_model=Notification)
def get_notification_read_endpoint(id: str):
    return read_notification(ObjectId(id))

@app.post("/notification/{id}/reply", response_model=Notification)
def create_notification_reply_endpoint(id: str, reply: NotificationReply):
    return reply_to_notification(ObjectId(id), reply)

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


@app.get("/orders/{email}/open", response_model=list[UserOrder])
def get_open_orders_endpoint(email: str): 
    return get_open_orders(email) 

@app.post("/orders/", response_model=UserOrder)
def create_user_order_endpoint(order: UserOrder): 
    return add_order(order) 

@app.get("/pop/")
def pop_endpoint():
    return burst_the_bubble()

@app.post("/news/reset")
def reset_all_news_endpoint(): 
    return reset_news() 

@app.get("/news/random", response_model=News)
def generate_random_news_endpoint(): 
    return generate_random_article() 
