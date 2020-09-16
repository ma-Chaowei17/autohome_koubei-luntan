# -*- coding: utf-8 -*-
"""

C2017-39


"""
import copy

import execjs
import scrapy
import time
from scrapy.conf import settings
from scrapy.mail import MailSender
import json
from scrapy.conf import settings
from ..items import echongdianItem
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import csv

website = 'weima'


#  curl http://192.168.1.249:6800/schedule.json -d project=baogang_tzr -d spider=kang_lianlian

class CarSpider(scrapy.Spider):
    name = website
    fans_urls = "https://zhixing.wm-imotor.com/zhixing/comment/list?postId={}&pageNo={}"
    start_url = "https://zhixing.wm-imotor.com/zhixing/community/recommendList?pageNo={}"

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.mailer = MailSender.from_settings(settings)
        self.counts = 0
        self.carnum = 800000
        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQL_SERVER', '192.168.1.94', priority='cmdline')
        settings.set('MYSQLDB_PASS', '94dataUser@2020', priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQLDB_USER', 'dataUser94', priority='cmdline')
        self.headers = {
            "User-Agent": "com.xiaopeng.mycarinfo/2.14.0 (6306; PCT-AL10; Android; 5.1.1; HUAWEI; androidstore)",
        }

    def start_requests(self):
        for i in range(1000):
            url = self.start_url.format(i + 1)
            yield scrapy.Request(url=url, dont_filter=True)

    def parse(self, response):
        data = json.loads(response.text)['data']['rows']
        for i in data:
            item = {}
            item['postId'] = i['postId']
            item['postTitle'] = i['postTitle']
            item['createTime'] = i['createTime']
            item['praiseCount'] = i['praiseCount']
            item['isReward'] = i['isReward']
            item['postShowCount'] = i['postShowCount']
            try:
                item['activityId'] = i['activityId']
            except:
                item['activityId'] = None
            try:
                item['activityName'] = i['activityName']
            except:
                item['activityName'] = None
            item['postLabelId'] = i['postLabelId']
            item['labelName'] = i['labelName']
            item['replyCount'] = i['replyCount']
            item['postSummary'] = i['postSummary']
            item['nickname'] = i['user']['nickname']
            item['mobile'] = i['user']['mobile']
            for i in range(25):
                used_item = copy.deepcopy(item)
                url = self.fans_urls.format(item['postId'], i + 1)
                yield scrapy.Request(url, meta={'item': used_item}, headers=self.headers, callback=self.fans_parse)

    def fans_parse(self, response):
        data = json.loads(response.text)['data']['rows']
        for i in data:
            item = response.meta['item']
            item["fans_creationDate"] =i["creationDate"]
            item["fans_nickname"] =i['user']["nickname"]
            item["fans_mobile"] =i['user']["mobile"]
            item["fans_commentContent"] =i["commentContent"]
            item["fans_sex"] =i['user']["sex"]
            item["grabtime"] = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            item["url"] = response.url
            item["statusplus"] =str(item['postLabelId'])+str(item['fans_creationDate'])+str(item['fans_mobile'])+str(item['fans_nickname'])+str(item['fans_commentContent'])
            yield item
