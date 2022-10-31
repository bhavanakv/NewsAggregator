
from pollData import scrapeData
from datetime import datetime
import logging

logger = logging.getLogger('scrapeData')


from apscheduler.schedulers.background import BackgroundScheduler

def start():
    """
    Function that is executed continuously every hour.
    This method is reponsible to scrape news data from all the blogs every hour and put them into DB.

    """
    scheduler = BackgroundScheduler()
    logger.info("Scheduled job started at: {0}".format(datetime.now()))
    scheduler.add_job(scrapeData.addDataToDB, 'interval', minutes=5)
    logger.info("Scheduled job executed successfully")
    scheduler.start()

