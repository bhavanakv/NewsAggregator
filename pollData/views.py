from operator import contains
from django.shortcuts import render
from django.http import HttpResponse
from pollData.models import Lastruntime, Newsblog, Scrapeddata
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs

# Create your views here.
def index(request):
    return render(request,'hello.html',{ 'name' : 'Bhavana'})

def lastRunTime(request,pk):
    runtime_obj = Lastruntime.objects.get(pk=pk)
    lastruntime = runtime_obj.lastscrapedtime
    data_obj = Scrapeddata.objects.all()
    news_titles = Newsblog.objects.values('name').distinct()
    news_titles = [title.get('name') for title in news_titles]
    data_from_db = []
    scraped_data = []
    for obj in data_obj:
        record = {
            "headline" : obj.headline,
            "description" : obj.description,
            "link" : obj.written_by,
            "blog_name" : obj.blog.name,
            "blog_link" : obj.blog.link
        }
        data_from_db.append(record)
    for title in news_titles:
        data = list(filter(lambda x: x.get('blog_name') == title, data_from_db))
        scraped_news = {
            "newsTitle" : title,
            "data" : data
        }
        scraped_data.append(scraped_news)
    
    context = {
        "lastRunTime" : lastruntime,
        "scrapedData" : scraped_data

    }
    return render(request, "pollData.html", context)

def updateRunTime():
    runtime_obj = Lastruntime.objects.get(pk=1)
    runtime_obj.lastscrapedtime = datetime.now()
    runtime_obj.save()

def scrapebyName(soup, name, blog_id, rows):
    
    if name == "BBC News":
        secondary_items = soup.find_all(True, {"class":["nw-c-top-stories__primary-item","nw-c-top-stories__secondary-item"]})
        for item in secondary_items:
            rows = rows + 1
            item_link = "https://bbc.com" + item.find("a")['href']
            item_heading = item.find("a").text
            if item.find(class_= "gs-c-promo-summary") is not None:
                item_description = item.find(class_= "gs-c-promo-summary").text
            else:
                item_description = ""
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            scrapedData.save()
    
            
    if name == "NBC News":
        for item in soup.find_all('h2', {"class": "tease-card__headline"}):
            rows = rows + 1
            item_link = item.a['href']
            item_heading = item.text
            item_page = requests.get(item_link)
            page_soup = bs(item_page.content, 'html.parser')
            item_description = ""
            for page_item in page_soup.find_all('div', {"class" : ["article-hero-headline"]}):
                descendants = page_item.descendants
                for d in descendants:
                    if d.name == 'div':
                        item_description = d.text
                
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            scrapedData.save()
    

    if name == "Wired":
        for item in soup.find_all('div', {"class": ["summary-item__content"]})[:6]:
            rows = rows + 1
            item_link = "https://wired.com" + item.a['href']
            item_heading = item.a.text
            item_description = item.find('div', {"class": "summary-item__dek"}).text
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            scrapedData.save()

            

def addScrapeData(request):
    newsblog_objs = Newsblog.objects.all()
    links = [(obj.name, obj.link, obj) for obj in newsblog_objs]
    data = Scrapeddata.objects.all()
    data.delete()
    rows = 0
    for link in links:
        page = requests.get(link[1])
        soup = bs(page.content, "html.parser")
        scrapebyName(soup, link[0], link[2], rows)
        rows = Scrapeddata.objects.count()

    updateRunTime()
        
    return render(request,'hello.html',{ 'name' : 'Bhavana'})
