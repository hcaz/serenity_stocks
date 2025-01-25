import math
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from AtlasClient import getClient
from userOrders import compute_open_orders
from stocks import tick_stocks


scheduler = BackgroundScheduler()
news_collection  = getClient().get_collection("serenity_stocks", "news")

def ticker():
    print(f"Running ticker at {time.time()}")
    timestamp = math.ceil(time.time())
    daySecond = timestamp % 160
    if daySecond > 120:
        if daySecond < 130:
            # fetch all news for this day
            all_news = news_collection.find({
                "timestamp": {
                    "$gt": timestamp - daySecond,
                    "$lt": timestamp - daySecond + 160,
                }
            })
            all_news = list(all_news)
            # if len(all_news) > 0:
            #     # if n docs returned chance to generate = 1/(n^2+1)
            # else:
                # first run
                # realocate budgets
                # if none returned generate new
        return
    tick_stocks()
    compute_open_orders()


# scheduler.add_job(ticker, IntervalTrigger(seconds=4))
