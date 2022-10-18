from django.apps import AppConfig


class PolldataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pollData'

    def ready(self):
        from pollData import scheduler, scrapeData
        scrapeData.addDataToDB()
        scheduler.start()
