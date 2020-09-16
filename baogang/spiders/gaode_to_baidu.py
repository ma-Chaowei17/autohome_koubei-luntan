# -*- coding: utf-8 -*-
"""

C2017-39


"""
import pandas as pd
import scrapy
from redis import Redis

import time
import logging
import json
from scrapy.conf import settings
import pymongo

website = 'gaode_to_baidu'


class CarSpider(scrapy.Spider):
    name = website
    start_urls = ["http://bj.gongpingjia.com/api/city-group-by-alphabet/"]
    custom_settings = {
        "ITEM_PIPELINES":{}
        ,"CONCURRENT_REQUESTS":20,
        "DOWNLOAD_DELAY":0
    }
    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 800000
        self.city_count = 0
        mongo_client = pymongo.MongoClient("192.168.1.94", 27017)
        db = mongo_client["api"]
        self.collection = db["gdapi_carrepair_2020"]
        self.collection_2 = db["gdapi_carrepair_2020_baidu"]

    def get_data_list(self):

        autohome = self.collection.find({}, {'_id': 0})
        list1 = []
        for i in autohome:
            list1.append(i)
        list1 = pd.DataFrame(list1)
        gd_dict = list1.to_dict(orient='records')
        return gd_dict

    def start_requests(self):
        gd_dict = self.get_data_list()
        for gd in gd_dict:
            url = "http://api.map.baidu.com/geoconv/v1/?coords=%s&from=1&to=5&ak=0nIp0ZxAyuSbIloGzSqZMK006GALOZMo" % (
                gd["location"])
            yield scrapy.Request(url=url,meta=gd)

    def baidu_lng(self,a):
        try:
            return str(a.split(",")[0])
        except:
            return ""

    def baidu_lat(self,a):
        try:
            return str(a.split(",")[1])
        except:
            return ""
    def parse(self, response):
        data =json.loads(response.text)
        gd =response.meta
        print(gd)
        gd["baidu_location"] = str(data["result"][0]["x"]) + "," + str(data["result"][0]["y"])
        gd["baidu_lng"] = self.baidu_lng(gd["baidu_location"])
        gd["baidu_lat"] = self.baidu_lat(gd["baidu_location"])
        print(gd)
        self.collection_2.insert(gd)