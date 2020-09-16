# -*- coding: UTF-8 -*-
import base64
import datetime
import json
import re

import requests
import scrapy
import time
import logging

website = 'zhilian'


# original
class CarSpider(scrapy.Spider):
    # basesetting
    name = website
    start_urls = [
        "https://jobs.zhaopin.com/all/"
    ]
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
    'baogang.proxy.zhilian': 543,
},
        "ITEM_PIPELINES" : {
},
                "COOKIES_ENABLED":False,
        "REDIRECT_ENABLED": False,
        "DUPEFILTER_DEBUG": True
    }


    def __init__(self, **kwargs):
        # args
        super(CarSpider, self).__init__(**kwargs)

        self.headers = {

            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36",
            "Referer": "https://jobs.zhaopin.com/all/"
        }


    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], headers=self.headers, dont_filter=True)

    def parse(self, response):
        print(response.request.headers)
