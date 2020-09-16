# -*- coding: utf-8 -*-
"""

C2017-40

"""
import json

import scrapy
from ..items import XinLang_KouBei
import time
from scrapy.conf import settings

website = 'xinlang_koubei'


class CarSpider(scrapy.Spider):
    name = website
    start_urls = "https://price.auto.sina.cn/api/paihangbang/getCommentScoreAlltype"
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

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers)

    def parse(self, response):
        koubei_all_list = json.loads(response.body)["data"]
        for index in range(len(koubei_all_list)):
            level = self.type_list[index]
            for data in koubei_all_list[index]["list"]:
                item = XinLang_KouBei()
                item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item["url"] = response.url
                item["id"] = data["id"]
                item["sub_brand_id"] = data["sub_brand_id"]
                item["sum_score"] = data["sum_score"]
                item["sample_size"] = data["sample_size"]
                item["space_score"] = data["space_score"]
                item["power_scoure"] = data["power_scoure"]
                item["control_score"] = data["control_score"]
                item["fuel_consumption_score"] = data["fuel_consumption_score"]
                item["comfort_score"] = data["comfort_score"]
                item["exterior_score"] = data["exterior_score"]
                item["interior_score"] = data["interior_score"]
                item["cost_performance_score"] = data["cost_performance_score"]
                item["create_at"] = data["create_at"]
                item["paiming"] = data["paiming"]
                item["pic"] = data["pic"]
                item["level"] = level
                item["statusplus"] = str(data) + level
                yield item
