import scrapy

class WikiSpider(scrapy.Spider):
    name = "wiki_spider"
    start_urls = ['https://www.wikipedia.org/']

    def parse(self, response):
        title = response.css('title::text').get()
        if title is not None:
            print("Title found: " + title)
        else:
            print("Title not found")

