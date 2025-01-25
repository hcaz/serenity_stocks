import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from stocks import tick_stocks


scheduler = BackgroundScheduler()

def ticker():
    print(f"Running ticker at {time.time()}")
    tick_stocks()

scheduler.add_job(ticker, IntervalTrigger(seconds=1))