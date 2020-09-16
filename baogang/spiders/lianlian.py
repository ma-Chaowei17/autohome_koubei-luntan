# -*- coding: utf-8 -*-
"""

C2017-39


"""
import scrapy
import time
from scrapy.conf import settings
from scrapy.mail import MailSender
import logging
import json
import re
import random
import hashlib
from hashlib import md5
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.conf import settings
from ..items import  LianlianItem
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import csv

website='kang_lianlian'
#  curl http://192.168.1.249:6800/schedule.json -d project=baogang_tzr -d spider=kang_lianlian

class CarSpider(scrapy.Spider):

    name=website
    start_urls = [
        "https://www.evchargeonline.com/site/station/list?operatorIds=&equipmentTypes=&payChannels=&isNewNantionalStandard=-1&isOpenToPublic=-1&isParkingFree=-1&longitude=121.50447&latitude=31.28671"
    ]


    def __init__(self,**kwargs):
        super(CarSpider,self).__init__(**kwargs)
        self.mailer=MailSender.from_settings(settings)
        self.counts=0
        self.carnum=800000
        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQL_SERVER', '192.168.1.94', priority='cmdline')
        settings.set('MYSQLDB_PASS', '94dataUser@2020', priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQLDB_USER', 'dataUser94', priority='cmdline')

    # https://www.evchargeonline.com/site/station/list?timestamp=1589766759813&operatorIds=&equipmentTypes=&payChannels=&isNewNantionalStandard=-1&isOpenToPublic=-1&isParkingFree=-1&longitude=108.024001&latitude=33.420001
    # https://www.evchargeonline.com/site/station/list?timestamp=1589770174004&operatorIds=&equipmentTypes=&payChannels=&isNewNantionalStandard=-1&isOpenToPublic=-1&isParkingFree=-1&longitude=108.024001&latitude=33.420001&radius=10000>
    def start_requests(self):
        # C:\Users\Administrator\Desktop\work_code\test
        # with open("/home/home/mywork/lianlian//SH_xy.csv") as f:
        with open(r"C:\Users\Administrator\Desktop\work_code\test\x_y.csv") as f:
            lines = csv.reader(f)
            for line in lines:
                if line[0] != "x":
                    tm = int(round(time.time() * 1000))
                    url = "https://www.evchargeonline.com/site/station/list?timestamp=%d&operatorIds=&equipmentTypes=&payChannels=&isNewNantionalStandard=-1&isOpenToPublic=-1&isParkingFree=-1&longitude=%s&latitude=%s&radius=10000" % (
                    tm, line[0], line[1])
                    yield scrapy.Request(url=url, meta={"lng":line[0], "lat":line[1]})

    def parse(self, response):
        data = json.loads(json.loads(response.body))
        print(data
              )
        for station in data["data"]["stations"]:
            item =  LianlianItem()
            item['grabtime'] = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            item['url'] = response.url
            item['status2'] = station["stationId"] + "-" + response.url
            item['payment'] = station["payment"]
            item['operatorLogo'] = station["operatorLogo"]
            item['operatorId'] = station["operatorId"]
            item['operatorName'] = station["operatorName"]
            item['stationId'] = station["stationId"]
            item['stationName'] = station["stationName"]
            item['electricityFee'] = station["electricityFee"]
            item['distance'] = station["distance"]
            item['directTotal'] = station["directTotal"]
            item['directAvaliable'] = station["directAvaliable"]
            item['alternatingTotal'] = station["alternatingTotal"]
            item['alternatingAvaliable'] = station["alternatingAvaliable"]
            item['parkFee'] = station["parkFee"]
            item['serviceFee'] = station["serviceFee"]
            item['stationLng'] = station["stationLng"]
            item['stationLat'] = station["stationLat"]
            item['stationLngBD'] = station["stationLngBD"]
            item['stationLatBD'] = station["stationLatBD"]
            item['stationType'] = station["stationType"]
            item['address'] = station["address"]
            item['pictures'] = station["pictures"]
            item['sitePicUrl'] = station["sitePicUrl"]
            item['statusplus'] = item["grabtime"] + "-" + str(item["stationId"]) + "-" + response.url + "-" + str(item['directAvaliable']) + "-" + str(item['alternatingAvaliable'])
            yield item
