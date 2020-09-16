# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import re
import time
from lxml import etree
from hashlib import md5
import requests
import scrapy
from fontTools.ttLib import TTFont
from redis import Redis
# from scrapy.conf import settings
from scrapy.utils.project import get_project_settings 
settings = get_project_settings()

from ..proxy import get_ug
from ..items import LuntanItem
from baogang.font import get_map

# 爬虫名
website = "kangkang_autohome_luntan"


# redis_cli = Redis(host="192.168.1.249", port=6379, db=2)


class AutohomeSpider(scrapy.Spider):
    name = website
    # allowed_domains = ['atuoheme']
    start_urls = ["https://club.autohome.com.cn/frontapi/bbs/getSeriesByLetter"]

    # 做一些配置的操作
    def __init__(self, **kwargs):
        # 比亚迪e3   5371      长安CS55 PLUS  5498  奕炫论坛 5103   哈弗H6论坛 包含运动版  2123  博越论坛
        super(AutohomeSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 2000000
        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQL_SERVER', '192.168.1.94', priority='cmdline')
        settings.set('MYSQLDB_PASS', '94dataUser@2020', priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQLDB_USER', 'dataUser94', priority='cmdline')
        self.font_map = {}
        self.headers = {'Referer': 'https://club.autohome.com.cn/',
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], headers=self.headers)

    # 实现翻页，并且进入下一个循环
    def parse(self, response):
        car_list = [
            '途观L新能源论坛', "探岳GTE插电混动论坛", "唐/唐新能源论坛", "宋Pro/宋Pro新能源论坛", "荣威RX5/RX5新能源论坛", "宝马X1新能源论坛",
            "帕萨特新能源论坛", "迈腾论坛", "雷凌双擎E+论坛", "汉论坛", "雅阁论坛", "凯美瑞论坛",
        ]
        try:
            results = json.loads(response.text)["result"]
        except:
            results = requests.get(url="https://club.autohome.com.cn/frontapi/bbs/getSeriesByLetter",
                                        headers=self.headers).json()["result"]
        random.shuffle(results)
        for brand_dict in results:
            car_urls = brand_dict["bbsBrand"]
            random.shuffle(car_urls)
            for car_url in car_urls:
                brand = car_url["bbsBrandName"]
                bbslit = car_url["bbsList"]
                random.shuffle(bbslit)
                for car in bbslit:
                    # print(car ,"-"*50)
                    car_id = car["bbsId"]
                    user_car = car["bbsName"]
                    # print(user_car)
                    if user_car in car_list:
                        url = "https://club.autohome.com.cn/frontapi/topics/getByBbsId?pageindex=1&pagesize=100&bbs=c&bbsid={}&fields=topicid%2Ctitle%2Cpost_memberid%2Cpost_membername%2Cpostdate%2Cispoll%2Cispic%2Cisrefine%2Creplycount%2Cviewcount%2Cvideoid%2Cisvideo%2Cvideoinfo%2Cqainfo%2Ctags%2Ctopictype%2Cimgs%2Cjximgs%2Curl%2Cpiccount%2Cisjingxuan%2Cissolve%2Cliveid%2Clivecover%2Ctopicimgs&orderby=topicid-".format(
                            car_id)
                        yield scrapy.Request(url=url, callback=self.page_turning,
                                             meta={"id": car_id, "user_car": user_car, "page": 1, "brand": brand},
                                             headers=self.headers)

    def deal_time(self, deal_time):
        # 一年 = 31536081
        a1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # print(a1)
        a2 = deal_time
        timeArray1 = time.strptime(a1, "%Y-%m-%d %H:%M:%S")
        timeArray2 = time.strptime(a2, "%Y-%m-%d %H:%M:%S")
        timeStamp1 = int(time.mktime(timeArray1))
        timeStamp2 = int(time.mktime(timeArray2))
        index = timeStamp1 - timeStamp2
        if index <= 31536081:
            logging.log(msg=(timeStamp1, "*" * 50, timeStamp2, True), level=logging.INFO)

            return True
        else:
            logging.log(msg=(timeStamp1, "*" * 50, timeStamp2, False), level=logging.INFO)

            return False

    def page_turning(self, response):
        # print(response.text)
        try:

            pinglun_url_dict = json.loads(response.text)
        except:
            yield scrapy.Request(url=response.url, callback=self.page_turning,
                                 meta=response.meta,
                                 headers=self.headers)
            return
        print(pinglun_url_dict["returncode"], "**" * 50)
        if pinglun_url_dict["returncode"] != 0:
            return
        else:
            for pinglun_url in pinglun_url_dict["result"]["list"]:
                index = self.deal_time(pinglun_url["postdate"])
                if index == False:
                    continue
                else:

                    yield scrapy.Request(url=pinglun_url["url"], callback=self.parse_luntan, headers=self.headers,
                                         meta=response.meta)
            url = "https://club.autohome.com.cn/frontapi/topics/getByBbsId?pageindex={}&pagesize=100&bbs=c&bbsid={}&fields=topicid%2Ctitle%2Cpost_memberid%2Cpost_membername%2Cpostdate%2Cispoll%2Cispic%2Cisrefine%2Creplycount%2Cviewcount%2Cvideoid%2Cisvideo%2Cvideoinfo%2Cqainfo%2Ctags%2Ctopictype%2Cimgs%2Cjximgs%2Curl%2Cpiccount%2Cisjingxuan%2Cissolve%2Cliveid%2Clivecover%2Ctopicimgs&orderby=topicid-"

            response.meta["page"] = response.meta["page"] + 1
            url = url.format(response.meta["page"], response.meta["id"], )
            yield scrapy.Request(url=url,
                                 callback=self.page_turning,
                                 meta=response.meta, headers=self.headers)

    def text_ttf(self, url):
        # font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "luntan.ttf") 
        font_path = '/home/home/baogang/baogang/baogang/luntan.ttf'
        User_Agent = {'User-Agent': get_ug()}
        try:
            text = requests.get(url=url, headers=User_Agent)
        except:
            logging.log(msg='Proxy request timeout Wait for two seconds', level=logging.INFO)
            return 0
        else:
            with open(font_path, "wb") as f:
                f.write(text.content)

            font_map = get_map(font_path)
            return font_map

    def get_click_num(self, data):
        url = "https://clubajax.autohome.com.cn/Detail/LoadX_Mini?topicId={}".format(data)

        text = requests.get(url=url, headers=self.headers).json()
        try:
            a = text["topicClicks"]["Views"]
        except:
            a = 0
        return a

    def parse_luntan(self, response):
        TFF_text_url = response.xpath("//style[@type='text/css']/text()").extract_first()
        url = re.findall(r"format\('embedded-opentype'\),url\('(.*?)'\) format\('woff'\)", TFF_text_url)
        if url == []:
            return
        if "k3.autoimg.cn" in url[0]:
            font_map = self.text_ttf("https:" + url[0])
        else:
            font_map = self.text_ttf("https://k3.autoimg.cn" + url[0])
        if font_map == 0:
            return
        item = LuntanItem()
        item["information_source"] = website
        item["brand"] = response.meta["brand"]
        item["title"] = response.xpath("//h1/div/text()").extract_first()
        item["grabtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["parsetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 处理content
        content_list = response.xpath("string(//div[@class='conttxt'])").getall()

        item["content"] = ""
        for content in content_list:
            if content == '':
                continue
            else:
                item["content"] += content.strip("\n").strip()
        for font in font_map.keys():
            old1 = '&#x' + font[3:].lower() + ';'
            old2 = r'\u' + font[3:].lower()
            item["content"] = re.sub(old1, font_map[font], item["content"])
            item['content'] = re.sub(old2, font_map[font], item["content"])
            item['content'] = re.sub(r'\xa0', ' ', item["content"])
            item['content'] = re.sub(r'&nbsp;', ' ', item["content"])

        item["url"] = response.url
        item["user_name"] = response.xpath("//ul[@class='maxw']/li/a/@title").extract_first()
        item["posted_time"] = response.xpath(
            "//span[contains(text(),'发表于')]/following-sibling::span[1]/text()").extract_first()
        item["user_car"] = response.xpath("//div[@class='consnav']/span[2]/a/text()").extract_first().strip("论坛")
        province = response.xpath("//a[@title='查看该地区论坛']/text()").extract_first().split()
        if len(province) == 2:
            item["province"] = province[0]
            item["region"] = province[1]
        else:
            item["province"] = province[0]
            item["region"] = None
        try:
            tieziid = re.findall(r"/(\d*)-1.html", response.url)[0]
        except:
            item["click_num"] = 0
        else:
            item["click_num"] = self.get_click_num(tieziid)
        item["reply_num"] = response.xpath("//font[@id='x-replys']/text()").extract_first()
        item["statusplus"] = str(item["user_name"]) + str(item["title"]) + str(item["posted_time"]) + str(
            item["province"]) + str(item["brand"]) + str(item["click_num"]) + str(item["reply_num"])
        item["content_num"] = response.xpath("//a[@title='查看']/text()").extract_first().split("帖")[0]
        if item["content"] == "":
            return
        else:
            yield item
            # print(item)
            # pass
