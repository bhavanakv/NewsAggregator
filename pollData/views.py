from django.shortcuts import render
from pollData.models import Lastruntime, Newsblog, Scrapeddata
from django.http import JsonResponse
from pollData import scrapeData
import logging

logger = logging.getLogger('scrapeData')

def index(request):
    """
    Default REST API to render a dummy html file
    """
    logger.info("Rendering the html file")
    return render(request,'hello.html',{ 'name' : 'Bhavana'})

def getScrapeData(request):
    """
    REST API to get the data from DB and return as a JSON response

    """
    logger.debug("Beginning to read the data from database")
    runtime_obj = Lastruntime.objects.get(pk=1)
    # Fetching last updated time
    lastruntime = runtime_obj.lastscrapedtime
    # Fetching scraped data from DB
    scraped_data = scrapeData.get_data()
    
    # Passing the fetched data as a JSON response
    context = {
        "lastRunTime" : lastruntime,
        "scrapedData" : scraped_data

    }
    logger.info("Rendering the scraped data into HTML file at time: " + str(lastruntime))
    return render(request, "pollData.html", context)

def addScrapeData(request):
    """
    REST API to add the data to DB

    """
    logger.info("Adding the data to DB")
    scrapeData.addDataToDB()
    logger.info("Updated the DB with latest data scraped from websites")

    # Sending JSON response after successful update to DB
    return JsonResponse({'status': 'OK', 'message': 'Scraped the data successfully'})

def getLastRunTime(request):
    """
    REST API to get the time when the scraping was last done

    """
    runtime = scrapeData.getLastRunTime()
    logger.info("Returning the last runtime as: {0}".format(runtime))
    return JsonResponse({'status': 'OK', 'lastRunTime': runtime})
