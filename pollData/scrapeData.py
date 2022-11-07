import requests
from bs4 import BeautifulSoup as bs
from pollData.models import Newsblog, Scrapeddata, Lastruntime
from datetime import datetime
import logging

logger = logging.getLogger('scrapeData')


def get_data():
    """
    Function to retrieve data from DB.
    The retrieved data from DB is parsed and returned as a JSON response.

    :return: List of headlines, their links and descriptions grouped by news website

    """
    logger.info("Retrieving data from DB")
    # Fetching scraped news data from DB
    data_obj = Scrapeddata.objects.all()
    # Fetching news blogs metadata
    news_titles = Newsblog.objects.values('name','link').distinct('name')
    news_titles = [(title.get('name'),title.get('link')) for title in news_titles]

    data_from_db = []
    scraped_data = []
    logger.info("Fetched {0} news headlines from DB".format(len(data_obj)))
    # Converting the data from DB into dictionary
    logger.debug("Started parsing the fetched data")
    for obj in data_obj:
        record = {
            "headline" : obj.headline,
            "description" : obj.description,
            "link" : obj.written_by,
            "blog_name" : obj.blog.name
        }
        data_from_db.append(record)
    # Making groups for each news blog and adding news data within each group 
    for title in news_titles:
        data = list(filter(lambda x: x.get('blog_name') == title[0], data_from_db))
        if title[0] == "NY Times":
            news_link = "https://www.nytimes.com/section/world"
        else:
            news_link = title[1]
        scraped_news = {
            "newsTitle" : title[0],
            "newsLink": news_link,
            "data" : data
        }
        scraped_data.append(scraped_news)
    logger.debug("Completed parsing the data")
    logger.info("Returning the fetched data from DB")
    return scraped_data

def updateRunTime():
    """
    Function to update the last updated time in DB.
    This time indicates the time when the new data is scraped and added to DB.
    
    """
    runtime_obj = Lastruntime.objects.get(pk=1)
    # Updating the last runtime to current time
    runtime_obj.lastscrapedtime = datetime.now()
    logger.info("Updating last updated time to: {0}".format(runtime_obj.lastscrapedtime))
    runtime_obj.save()

def getLastRunTime():
    """
    Function to fetch the last runtime. This time indicates when the scraping was done and headlines were saved into DB successfully.
    
    """
    runtime_obj = Lastruntime.objects.get(pk=1)
    logger.debug("Fetched the last runtime as: {0}".format(runtime_obj.lastscrapedtime))
    return runtime_obj.lastscrapedtime

def addDataToDB():
    """
    Function to scrape and add the news data for each news blog to DB.

    """
    logger.debug("Deleting the existing data before adding new data")
    newsblog_objs = Newsblog.objects.all()
    links = [(obj.name, obj.link, obj) for obj in newsblog_objs]
    data = Scrapeddata.objects.all()
    # Deleting all the records in DB before adding new news data
    data.delete()
    rows = 0
    for link in links:
        logger.debug("Scraping started for webpage: {0}".format(link))
        # Retreiving the content of news blog
        page = requests.get(link[1])
        # If the content is json, then REST API is provided by news blog, otherwise we need to web scrape the blog
        if page.headers.get('Content-Type') == 'application/json':
            # Fetch the json content
            response = page.json()
            scrapeByApi(response, link[0], link[2], rows)
        else:
            # Parse the content using beautifulSoup html parser
            soup = bs(page.content, "html.parser")
            scrapebyWebpage(soup, link[0], link[2], rows)
        # Updating the rows after one blog is scraped
        rows = Scrapeddata.objects.count()

    updateRunTime()

def scrapebyWebpage(soup, name, blog_id, rows):
    """
    Function to perform webscraping and save the data into DB.

    """
    
    # Scraping differently for each news blog
    if name == "BBC News":
        # Fetch all the primary items from the home page
        secondary_items = soup.find_all(True, {"class":["nw-c-top-stories__primary-item","nw-c-top-stories__secondary-item"]})[:6]
        for item in secondary_items:
            rows = rows + 1
            # Link for article
            item_link = "https://bbc.com" + item.find("a")['href']
            # Headline of the article
            item_heading = item.find("a").text
            # Scraping short description of the article in home page 
            if item.find(class_= "gs-c-promo-summary") is not None:
                item_description = item.find(class_= "gs-c-promo-summary").text
            else:
                logger.debug("Could not find summary for link: {0}".format(item_link))
                item_description = ""
            # Saving the data into DB
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            logger.debug("Saving data: {0} in row: {1}".format(scrapedData.headline, rows))
            scrapedData.save()
    
            
    if name == "NBC News":
        # Fetching all the cards on which news data is described present on home page
        for item in soup.find_all('h2', {"class": "tease-card__headline"})[:5]:
            rows = rows + 1
            # Link for article
            item_link = item.a['href']
            # Headline of the article
            item_heading = item.text
            # Description is not available on home page, so to get short description, we need to go to the link. 
            # Again the page has to be scraped to get the description
            item_page = requests.get(item_link)
            page_soup = bs(item_page.content, 'html.parser')
            item_description = ""
            for page_item in page_soup.find_all('div', {"class" : ["article-hero-headline"]}):
                # Fetching the children of the tag to get description
                descendants = page_item.descendants
                for d in descendants:
                    if d.name == 'div':
                        item_description = d.text

            # Saving the data into DB 
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            logger.debug("Saving data: {0} in row: {1}".format(scrapedData.headline, rows))
            scrapedData.save()
    

    if name == "Wired":
        # Fetching all the items given as a list in the most recents webpage
        for item in soup.find_all('div', {"class": ["summary-item__content"]})[:6]:
            rows = rows + 1
            # Link for article
            item_link = "https://wired.com" + item.a['href']
            # Headline of the article
            item_heading = item.a.text
            if(item.find('div', {"class": "summary-item__dek"}) is not None):
                item_description = item.find('div', {"class": "summary-item__dek"}).text
            else:
                # Description is not available on home page, so to get short description, we need to go to the link. 
                # Again the page has to be scraped to get the description
                item_page = requests.get(item_link)
                page_soup = bs(item_page.content, 'html.parser')
                if page_soup.find('div',{"class" : ["content-header__accreditation"]}):
                    # Fetching the first child of the tag to get description
                    item_description = page_soup.find_all('div',{"class" : ["content-header__accreditation"]})[0].div.text
                else:
                    item_description = " "
            
            # Saving the data into DB
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            logger.debug("Saving data: {0} in row: {1}".format(scrapedData.headline, rows))
            scrapedData.save()

    
    if name == "Forbes":
        # Fetching all the items given as a list in the most recents webpage
        for item in soup.findAll('article', {"class":"stream-item"})[:6]:
            rows = rows + 1
            # Link for article
            item_link = item.a['href']
            # Headline of the article
            item_heading = item.a.text
            if item.find('div',{"class":"stream-item__description"}) is not None:
                item_description = item.find('div',{"class":"stream-item__description"}).text
            else:
                item_description = " "
            
            # Saving the data into DB
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            logger.debug("Saving data: {0} in row: {1}".format(scrapedData.headline, rows))
            scrapedData.save()
            
def scrapeByApi(data, name, blog_id, rows):
    """
    Function to use REST API given by few blogs to retrieve news data and store in DB

    """
    if name == "NY Times":
        # Fetching all the articles from the response that contain various types of news data
        results = [result for result in data['results'] if result['title'] is not None and len(result['title']) > 1 and result['item_type'] == 'Article'][:6]
        for result in results:
            rows = rows + 1
            # Headline of the article
            item_heading = result['title']
            item_description = result['abstract']
            # Link for article
            item_link = result['url']
            
            # Saving the data into DB
            scrapedData = Scrapeddata(id=rows,headline=item_heading, description=item_description, timestamp=datetime.now(), blog=blog_id, written_by=item_link)
            logger.debug("Saving data: {0} in row: {1}".format(scrapedData.headline, rows))
            scrapedData.save()