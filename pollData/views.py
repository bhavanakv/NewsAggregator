from django.shortcuts import render
from pollData.models import Lastruntime, Newsblog, Scrapeddata
from django.http import JsonResponse
from pollData import scrapeData

# Create your views here.
def index(request):
    return render(request,'hello.html',{ 'name' : 'Bhavana'})

def lastRunTime(request,pk):
    runtime_obj = Lastruntime.objects.get(pk=pk)
    lastruntime = runtime_obj.lastscrapedtime
    scraped_data = scrapeData.get_data()
    
    context = {
        "lastRunTime" : lastruntime,
        "scrapedData" : scraped_data

    }
    return render(request, "pollData.html", context)

def addScrapeData(request):
    
    scrapeData.addDataToDB()
    return JsonResponse({'status': 'OK', 'message': 'Scraped the data successfully'})
