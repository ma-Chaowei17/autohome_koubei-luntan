# month: 10# -*- coding: utf-8 -*-
# https://price.auto.sina.cn/api/paihangbang/getDateList  时间接口
# https://price.auto.sina.cn/api/paihangbang/getSalesByDateAllTypes/?year=2019&month=10 接口
# year: 2019
# """
#
# C2017-40
#
# """
import json

import requests
import scrapy
from ..items import XinLang_XiaoShou
import time
from scrapy.conf import settings

website = 'xinlang_xiaoshou'


class CarSpider(scrapy.Spider):
    name = website
    start_urls = "https://price.auto.sina.cn/api/paihangbang/getSalesByDateAllTypes/?year={}&month={}"
    type_list = ["总榜", "轿车", "SUV", "MPV", "新能源"]
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

    def get_year(self):
        url = "https://price.auto.sina.cn/api/paihangbang/getDateList"
        year_dict = requests.get(url=url, headers=self.headers).json()["data"]
        return year_dict

    def start_requests(self):
        year_list = self.get_year()
        for i in year_list[0:1]:
            url = self.start_urls.format(i["year"], i["month"])
        yield scrapy.Request(url=url, headers=self.headers)

    def parse(self, response):
        koubei_all_list = json.loads(response.body)["data"]
        for index in range(len(koubei_all_list)):
            level = self.type_list[index]
            for data in koubei_all_list[index]["list"]:
                # print("*"*50)
                # print(data)
                item = XinLang_XiaoShou()
                item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item["url"] = response.url
                item["id"] = data["id"]
                item["name"] = data["name"]
                item["pic"] = data["pic"]
                item["sales_volume"] = data["sales_volume"]
                item["paiming"] = data["paiming"]
                item["last_paiming"] = data["last_paiming"]
                item["max_sales_month"] = data["max_sales_month"]
                try:
                    item["isupper"] = data["isupper"]
                except:
                    item["isupper"] = data["issupper"]
                item["year_sales_volume"] = data["year_sales_volume"]
                item["list"] = str(data["list"])
                item["statusplus"] = str(data) + level
                item["level"] = level
                # print(item)
                yield item
