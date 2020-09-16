# https://www.autohome.com.cn/car/


import json

import requests
import scrapy
from ..items import Autohome_depreciate
import time
from scrapy.conf import settings

website = 'autohome_depreciate'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = "https://www.autohome.com.cn/aspx/GetDealerInfoByCityIdNew.aspx?cityid=310100"
    level = ["推荐"
        , "SUV"
        , "小型车"
        , "紧凑型车"
        , "中型车"
        , "大型车"
        , "MPV"]
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
        level_list = response.xpath(
            "//ul[@class='athm-tab athm-tab--stacked']//li[@class='athm-tab__item']/a/text()").extract()
        car_list = response.xpath("//div[contains(@id,'buycar-')]")
        for i in range(len(car_list)):
            level = level_list[i]
            for z in car_list[i].xpath('.//dl//dd'):
                # print(z)
                item = Autohome_depreciate()
                item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item["url"] = response.url
                item["series"] = z.xpath(".//span[1]/a/text()").extract_first()
                item["level"] = level
                item["fudu"] = z.xpath(".//span[3]/a/text()").extract_first()
                item["price"] = z.xpath(".//span[2]/a/text()").extract_first()
                # print(item)
                item["statusplus"] = str(item["price"]) + str(item["fudu"]) + str(item["series"])
                yield item
