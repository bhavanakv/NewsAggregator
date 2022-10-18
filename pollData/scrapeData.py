import requests
from bs4 import BeautifulSoup as bs
from pollData.models import Newsblog, Scrapeddata, Lastruntime
from datetime import datetime

def get_data():
    data_obj = Scrapeddata.objects.all()
    news_titles = Newsblog.objects.values('name','link').distinct('name')
    news_titles = [(title.get('name'),title.get('link')) for title in news_titles]
    data_from_db = []
    scraped_data = []
    for obj in data_obj:
        record = {
            "headline" : obj.headline,
            "description" : obj.description,
            "link" : obj.written_by,
            "blog_name" : obj.blog.name
        }
        data_from_db.append(record)
    for title in news_titles:
        data = list(filter(lambda x: x.get('blog_name') == title[0], data_from_db))
        if title[0] == "NY Times":
            news_link = "https://www.nytimes.com/"
        else:
            news_link = title[1]
        scraped_news = {
            "newsTitle" : title[0],
            "newsLink": news_link,
            "data" : data
        }
        scraped_data.append(scraped_news)
    return scraped_data


def updateRunTime():
    runtime_obj = Lastruntime.objects.get(pk=1)
    runtime_obj.lastscrapedtime = datetime.now()
    runtime_obj.save()

def addDataToDB():
    newsblog_objs = Newsblog.objects.all()
    links = [(obj.name, obj.link, obj) for obj in newsblog_objs]
    data = Scrapeddata.objects.all()
    data.delete()
    rows = 0
    for link in links:
        page = requests.get(link[1])
        if page.headers.get('Content-Type') == 'application/json':
            response = page.json()
            scrapeByApi(response, link[0], link[2], rows)
        else:
            soup = bs(page.content, "html.parser")
            scrapebyWebpage(soup, link[0], link[2], rows)
        rows = Scrapeddata.objects.count()

    updateRunTime()

def scrapebyWebpage(soup, name, blog_id, rows):
    
    if name == "BBC News":
        secondary_items = soup.find_all(True, {"class":["nw-c-top-stories__primary-item","nw-c-top-stories__secondary-item"]})[:6]
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

        for item in soup.find_all('h2', {"class": "tease-card__headline"})[:5]:
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
            if(item.find('div', {"class": "summary-item__dek"}) is not None):
                item_description = item.find('div', {"class": "summary-item__dek"}).text
            else:
                item_description = " "
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            scrapedData.save()

    
    if name == "Forbes":
        for item in soup.findAll('article', {"class":"stream-item"})[:6]:
            rows = rows + 1
            item_link = item.a['href']
            item_heading = item.a.text
            if item.find('div',{"class":"stream-item__description"}) is not None:
                item_description = item.find('div',{"class":"stream-item__description"}).text
            else:
                item_description = " "
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            scrapedData.save()
            

def scrapeByApi(data, name, blog_id, rows):
    if name == "NY Times":
        results = [result for result in data['results'] if result['title'] is not None and len(result['title']) > 1 and result['item_type'] == 'Article'][:6]
        for result in results:
            rows = rows + 1
            item_heading = result['title']
            item_description = result['abstract']
            item_link = result['url']
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            scrapedData.save()