import math
import random
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from threading import Thread


from AtlasClient import getClient
from newsGenerator import generate_random_article
from notifications import generate_competitor_notice, generate_podcaster_notice
from userOrders import compute_open_orders
from stocks import tick_stocks


scheduler = BackgroundScheduler()
news_collection  = getClient().get_collection("serenity_stocks", "news")

is_trading_open = True

def ticker():
    global is_trading_open
    timestamp = math.ceil(time.time())
    daySecond = timestamp % 160

    # random number between 0 and 2
    random_int = random.randint(0, 1000)
    if random_int % 100 == 0:
        Thread(target=generate_random_article).start()

    if random_int % 10 == 0:
        print("send message from clippy to random group of players")

    if random_int % 50 == 0:
        print("send message from conspirator to random player that hasn't been engaged with them yet")

    if random_int % 50 == 0:
        print("send message from competitor to random player. will continue same message thread")
        Thread(target=generate_competitor_notice).start()

    if daySecond > 120:
        if is_trading_open:
            is_trading_open = False
            Thread(target=generate_podcaster_notice).start()
        # else:
        #     random_int = random.randint(0, ((daySecond-119)^2) + 1)
        #     if random_int == 1:
        #         # if n docs returned chance to generate = 1/(n^2+1)
        #         # TODO: generate notifications
        #         Thread(target=generate_random_article).start()
    else:
        is_trading_open = True
        Thread(target=tick_stocks).start()
        compute_open_orders()


scheduler.add_job(ticker, IntervalTrigger(seconds=2))
