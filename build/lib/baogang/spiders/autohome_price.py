# https://www.autohome.com.cn/car/


import json

import requests
import scrapy
from ..items import Autohome_price
import time
from scrapy.conf import settings

website = 'autohome_price'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = ["https://www.autohome.com.cn/car/"]
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

    def add_url(self):
        url = "https://www.autohome.com.cn/grade/carhtml/{}.html"
        car_list = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
                    "V", "W ", "X", "Y", "Z"]
        for i in car_list:
            self.start_urls.append(url.format(i))

    def start_requests(self):
        self.add_url()
        for i in self.start_urls:
            yield scrapy.Request(url=i, headers=self.headers, )

    def parse(self, response):
        if response.url == "https://www.autohome.com.cn/car/":
            brand_list = response.xpath("//div[@id='htmlA']//dl")
        else:
            brand_list = response.xpath("//dl")
        for i in brand_list:
            brand = i.xpath(".//dt//div//a/text()").extract_first()
            for x in i.xpath(".//dd//div[@class='h3-tit']"):
                factory = x.xpath(".//text()").extract_first()
                for a in x.xpath(".//following-sibling::ul[1]//li"):
                    series = a.xpath(".//h4/a/text()").extract_first()
                    url = a.xpath(".//h4/a/@href").extract_first()
                    if url == None:
                        continue
                    meta = {
                        "brand": brand,
                        "factory": factory,
                        "series": series,
                        "url ": "https:" + url,
                    }
                    # print(brand, factory, series, url)

                    yield scrapy.Request(url="https:" + url, headers=self.headers, meta=meta, callback=self.car_parse)
                    print(brand, factory, series, url)

    def car_parse(self, response):
        item = Autohome_price()
        item["pinfen"] = str(dict(zip(response.xpath("//ul[contains(@class,'rank-list')]//span[2]/a/text()").extract(),
                                      response.xpath(
                                          "//ul[contains(@class,'rank-list')]//span[3]/a/text()").extract())))
        item["price"] = response.xpath("//dl[contains(@class,'information-price')]/dd[1]//a[1]/text()").extract_first()
        item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["brand"] = response.meta["brand"]
        item["url"] = response.url
        item["factory"] = response.meta["factory"]
        item["series"] = response.meta["series"]
        item["kongjian"] = str(dict(
            zip(response.xpath("//span[contains(text(),'空间')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'空间')]/../span[@class='item-place']/a/text()").extract())))
        item["dongli"] = str(dict(
            zip(response.xpath("//span[contains(text(),'动力')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'动力')]/../span[@class='item-place']/a/text()").extract())))
        item["caokong"] = str(dict(
            zip(response.xpath("//span[contains(text(),'操控')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'操控')]/../span[@class='item-place']/a/text()").extract())))
        item["youhao"] = str(dict(
            zip(response.xpath("//span[contains(text(),'油耗')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'油耗')]/../span[@class='item-place']/a/text()").extract())))
        item["shushixing"] = str(dict(
            zip(response.xpath("//span[contains(text(),'舒适性')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'舒适性')]/../span[@class='item-place']/a/text()").extract())))
        item["waiguan"] = str(dict(
            zip(response.xpath("//span[contains(text(),'外观')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'外观')]/../span[@class='item-place']/a/text()").extract())))
        item["neishi"] = str(dict(
            zip(response.xpath("//span[contains(text(),'内饰')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'内饰')]/../span[@class='item-place']/a/text()").extract())))
        item["xingjiabi"] = str(dict(
            zip(response.xpath("//span[contains(text(),'性价比')]/../span[@class='item-score']/a/text()").extract(),
                response.xpath("//span[contains(text(),'性价比')]/../span[@class='item-place']/a/text()").extract())))
        item["statusplus"] = response.text+str(1111511)
        # print(item)
        yield item
