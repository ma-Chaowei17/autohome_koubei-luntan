import json
import re

import requests
import scrapy
from ..items import XinLang_XiaoLiang
import time
from scrapy.conf import settings

website = 'xinlang_xiaoliang'


class CarSpider(scrapy.Spider):
    name = website
    # http://db.auto.sina.com.cn/372/
    start_urls = "http://db.auto.sina.com.cn/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://auto.sina.com.cn"
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
        brand_list = response.xpath("//dl")
        for brand in brand_list:
            brand_name = brand.xpath(".//dt/a/text()").extract_first()
            for chexi in brand.xpath(".//dd")[1::]:
                series = chexi.xpath('.//a/text()').extract_first()
                series_url = chexi.xpath('.//a/@href').extract_first()
                meta = {
                    "series": series,
                    "series_url": series_url,
                    "brand_name": brand_name
                }
                if "html" in series_url:
                    continue
                else:
                    # series_url="http://db.auto.sina.com.cn/372/"
                    yield response.follow(url=series_url, headers=self.headers, meta=meta, callback=self.car_parse)
        # yield response.follow(url=series_url, headers=self.headers,  callback=self.car_parse)

    def car_parse(self, response):
        item = XinLang_XiaoLiang()
        # print(response.text)
        item["series"] = response.meta["series"]
        item["series_url"] = response.meta["series_url"]
        item["brand_name"] = response.meta["brand_name"]
        item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["sales_month"] = str({response.xpath(
            "//li[@class='monthsales']/div/div[@class='txt']/text()").extract_first(): response.xpath(
            "//li[@class='monthsales']/div/div[@class='num']/text()").extract_first()})
        item["sales_year"] = str({response.xpath(
            "//li[@class='yearsales']/div/div[@class='txt']/text()").extract_first(): response.xpath(
            "//li[@class='yearsales']/div/div[@class='num']/text()").extract_first()})
        try:
            item["transaction_price"] = str({response.xpath(
                "//li[@class='monthprice']/div/div[@class='txt']/text()").extract_first(): response.xpath(
                "//li[@class='monthprice']/div/div[@class='num']/text()").extract_first()})
        except:
            item["transaction_price"] = str({response.xpath(
                "//li[@class='monthprice']/div/div[@class='txt']/text()").extract_first(): response.xpath(
                "//li[@class='monthprice']/div/div[@class='num']/text()").extract_first()})
        try:
            chengjiao = re.findall(r'var chenjiao_val = (.*);', response.text)[0]
            xiaoliang = re.findall(r'var xiaoliang_val = (.*);', response.text)[0]
            month = re.findall(r'chenjiao_month = (.*);', response.text)[0]

        except:
            item["chenjiao_val"] = "{}"
            item["xiaoliang_val"] = "{}"
        else:
            item["chenjiao_val"] = str(dict(zip(eval(month), eval(chengjiao))))
            item["xiaoliang_val"] = str(dict(zip(eval(month), eval(xiaoliang))))
        item["zonghe_rank"] = str(response.xpath("//div[@class='top10_list']/ul[1]/li//span/text()").extract())
        item["anquan_rank"] = str(response.xpath("//div[@class='top10_list']/ul[2]/li//span/text()").extract())
        item["xingneng_rank"] = str(response.xpath("//div[@class='top10_list']/ul[3]/li//span/text()").extract())
        item["youhao_rank"] = str(response.xpath("//div[@class='top10_list']/ul[4]/li//span/text()").extract())
        item["kongjian_rank"] = str(response.xpath("//div[@class='top10_list']/ul[5]/li//span/text()").extract())
        item["shushi_rank"] = str(response.xpath("//div[@class='top10_list']/ul[6]/li//span/text()").extract())
        item["renji_rank"] = str(response.xpath("//div[@class='top10_list']/ul[7]/li//span/text()").extract())
        item["contend_car"] = str(response.xpath("//ul[@class='clearfix']/li//div[@class='txt']/a/text()").extract())
        item["statusplus"] = item["url"] + str(item["sales_month"]) + str(item["sales_year"]) + str(
            item["transaction_price"]) + str(item["chenjiao_val"]) + str(item["xiaoliang_val"])
        # print(item)
        yield item
