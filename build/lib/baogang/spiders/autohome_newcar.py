# https://www.autohome.com.cn/car/


import json

import requests
import scrapy
from ..items import Autohome_newcar
import time
from scrapy.conf import settings

website = 'autohome_newcar'


class CarSpider(scrapy.Spider):
    name = website
    start_urls = "https://www.autohome.com.cn/aspx/GetFeedNewsByTab.aspx?"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.autohome.com.cn"
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 800000
        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'baogang', priority='cmdline')

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers, )

    def parse(self, response):
        for i in response.xpath("//div[@class='timeline-wrap']/div"):
            item = Autohome_newcar()
            item["grade_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["posted_time"] = i.xpath("./div//p[1]//span/text()").extract_first()
            item["url"] = response.url
            item["car"] = i.xpath("./div//p[2]//a/text()").extract_first()
            item["statusplus"] = item["car"] + item["posted_time"]
            yield item
            # print(item)
