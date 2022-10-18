
from pollData import scrapeData
from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrapeData.addDataToDB, 'interval', minutes=5)
    scheduler.start()

