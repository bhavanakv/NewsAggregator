import requests
from bs4 import BeautifulSoup as bs

class ScrapeData:

    def bbc(self, link):
        page = requests.get(link)
        soup = bs(page.content, "html.parser")
        secondary_items = soup.find_all(True, {"class":["nw-c-top-stories__primary-item","nw-c-top-stories__secondary-item"]})
        for item in secondary_items:
            print(item.find("a")['href'])
            print(item.find("a").text)
            print(item.find(class_= "gs-c-promo-summary").text)

if __name__== "__main__":
    print("Started scraping")
    obj = ScrapeData()
    obj.bbc("https://www.bbc.com/news")