# https://www.autohome.com.cn/car/


import json

import requests
import scrapy
from ..items import Autohome_jiangjia
import time
from scrapy.conf import settings

website = 'autohome_jiangjia'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = "https://buy.autohome.com.cn/Car/GetCarListModel?brandid=0&seriesid=0&specid=0&pid=310000&cid=310100&serieslevel=0&pricescope=0&low=0&high=0&islastweek=0&ishasallowance=0&ishasgift=0&orderby=0&sortorder=0&searchtype=0&page={}&q=&ChannelIds="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.autohome.com.cn"
    }
    index = True

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 800000
        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'baogang', priority='cmdline')

    def start_requests(self):
        for i in range(500):
            if self.index == True:
                yield scrapy.Request(url=self.start_urls.format(i + 1), headers=self.headers)
            else:
                return

    def parse(self, response):
        content_dict = json.loads(response.text)["SeriesPriceModel"]["List"]
        if content_dict == []:
            self.index = False

        for i in content_dict:
            item = Autohome_jiangjia()
            item["grade_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["url"] = response.url
            item["MaxOriginalPrice"] = i["MaxOriginalPrice"]
            item["MaxPriceOff"] = i["MaxPriceOff"]
            item["MaxPriceOffSpecId"] = i["MaxPriceOffSpecId"]
            item["MinOriginalPrice"] = i["MinOriginalPrice"]
            item["SeriesId"] = i["SeriesId"]
            item["SeriesImg"] = i["SeriesImg"]
            item["SpecNumber"] = i["SpecNumber"]
            item["SeriesName"] = i["SeriesName"]
            item["statusplus"] = str(i)
            # print(item)
            yield item
