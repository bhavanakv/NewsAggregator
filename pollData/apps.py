from django.apps import AppConfig
import logging

logger = logging.getLogger('scrapeData')

class PolldataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pollData'

    def ready(self):
        """
        Function executed when the application is started.
        The news data is scraped and put into DB

        """
        from pollData import scheduler, scrapeData
        scrapeData.addDataToDB()
        logger.info("Data added to DB successfully after initial scraping")
        scheduler.start()
