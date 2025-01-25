import math
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from userOrders import compute_open_orders
from stocks import tick_stocks


scheduler = BackgroundScheduler()

def ticker():
    print(f"Running ticker at {time.time()}")
    timestamp = math.ceil(time.time())
    daySecond = timestamp % 160
    if daySecond > 120:
        if daySecond < 130:
            # fetch all news for this day
            # if none returned generate new
            # if n docs returned chance to generate = 1/(n^2+1)
            print("create news?")
        return
    tick_stocks()
    compute_open_orders()


scheduler.add_job(ticker, IntervalTrigger(seconds=4))