
import json
import math
import random
import time
from typing import Optional
from dotenv import dotenv_values
from AtlasClient import getClient
from NewsOutlet import NewsOutlet
from Stock import Stock
from UserOrder import UserOrder
import google.generativeai as genai


config = dotenv_values(".env")
GEMINI_API_KEY = config["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

news_outlets_collection = getClient().get_collection("serenity_stocks", "news_outlets")
news_collection = getClient().get_collection("serenity_stocks", "news")
stocks_collection = getClient().get_collection("serenity_stocks", "stocks")
user_orders_collection = getClient().get_collection("serenity_stocks", "user_orders")

def reset_news():
    news_outlets_collection.delete_many({})
    news_collection.delete_many({})

    myOutlets = []
    with open("news_outlets.json", "r") as json_file:
        data = json.load(json_file)
        for outlet_map in data:
            outlet = NewsOutlet(
                name = outlet_map['name'], 
                tone = outlet_map['tone'], 
                style = outlet_map['style'],
                bias = outlet_map['bias'],
                positive_stocks = outlet_map['positive_stocks'] if "positive_stocks" in outlet_map else [],
                negative_stocks = outlet_map['negative_stocks'] if "negative_stocks" in outlet_map else [],
                positive_categories = outlet_map['positive_categories'] if "positive_categories" in outlet_map else [],
                negative_categories = outlet_map['negative_categories'] if "negative_categories" in outlet_map else [],
            )
            myOutlets.append(outlet.dict())

    news_outlets_collection.insert_many(myOutlets)
    return

def generate_random_article(outlet: Optional[NewsOutlet] = None):
    if outlet is None:
        outlet = news_outlets_collection.aggregate([
            {"$sample": {"size": 1}}
        ])
    if outlet:
        outlet = NewsOutlet(**next(outlet))
    else:
        return
    
    timestamp = math.ceil(time.time())
    daySecond = timestamp % 160
    target_stock = stocks_collection.aggregate([
        {"$sample": {"size": 1}}
    ])
    target_stock = Stock(**next(target_stock))
    recent_orders = user_orders_collection.find({
        "symbol": target_stock.symbol,
        "completed_at": {
            "$gt": timestamp - daySecond,
            "$lt": timestamp - daySecond + 160,
        },
    }).sort("quantity")

    target = "stock" if random.random() > 0.5 else "category"

    buyer_info = []
    for order in recent_orders:
        order = UserOrder(**order)
        buyer_info.append("> " + order.email + ": " + order.quantity+"\n")

    buyer_info = ''.join(buyer_info)

    response = model.generate_content("You are a writer for " + outlet.name + " about movements in the stock market.\n\nYour general tone is " + outlet.tone + ". You are writing to an audience of players who are in charge of managing investment funds but the readers should never be addressed directly. You should write with a style that is " + outlet.style + ". You have the following biases: " + outlet.bias +"\n\nCompose a short article commentry on the " + target + (target_stock.name if target == "stock" else target_stock.category) + ((". It may be relevant to mentioned the top buyers of this stock, if used, please attempt to anonymise but poorly so they are still mostly readable:\n" + buyer_info) if target == "stock" else "") + ". Do not include a title, only the body text which should be no longer than 250 characters over multiple lines and matches your personality prompt, you should end the article with an open ended question related to the stock.\n\nRemember to stay within the character of a writer commenting on stocks during the dot com boom. Use a language and tone appropriate to that era but in a professional manner, and be mindful this game is about lack of ethics and morals which the player has to pick.")
    message = response.text
    print(message)
    
    return