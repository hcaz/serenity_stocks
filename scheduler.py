import math
import random
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from AtlasClient import getClient
from newsGenerator import generate_random_article
from userOrders import compute_open_orders
from stocks import tick_stocks


scheduler = BackgroundScheduler()
news_collection  = getClient().get_collection("serenity_stocks", "news")

is_trading_open = True

def ticker():
    print(f"Running ticker at {time.time()}")
    timestamp = math.ceil(time.time())
    daySecond = timestamp % 160
    if daySecond > 120:
        if is_trading_open:
            is_trading_open = False
            generate_random_article()
        else:
            random_int = random.randint(0, ((daySecond-119)^2) + 1)
            if random_int == 1:
                # if n docs returned chance to generate = 1/(n^2+1)
                generate_random_article()
    else:
        is_trading_open = True
        tick_stocks()
        compute_open_orders()


# scheduler.add_job(ticker, IntervalTrigger(seconds=4))
