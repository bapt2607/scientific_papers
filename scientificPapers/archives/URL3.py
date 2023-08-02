import scrapy
from scrapy_splash import SplashRequest

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ["https://www.sciencedirect.com/science/article/pii/S136184151730155X"]  # ajoutez d'autres URL ici
    custom_settings = {
        "LOG_LEVEL" : "DEBUG",
        "SPLASH_URL" : "http://localhost:8050",
        "DOWNLOADER_MIDDLEWARES" : {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        "SPIDER_MIDDLEWARES" : {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        "DUPEFILTER_CLASS" : 'scrapy_splash.SplashAwareDupeFilter',
    }

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 10})

    def parse(self, response):
        title = response.css('span.title-text').get(default="Title not found")
        print("Title: ", title)
