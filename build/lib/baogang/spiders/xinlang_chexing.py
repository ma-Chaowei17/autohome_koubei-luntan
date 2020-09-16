# ttps://data.auto.sina.com.cn/api/shengliang/getSerialTop/2017/19/2/   关注指数
# https://data.auto.sina.com.cn/api/shengliang/getSldaylist/2184,2987,626/1/ 近期走势
# https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 日期
# https://data.auto.sina.com.cn/api/shengliang/getCurTop/2/5000/ 全部数据 但是没有分类

import json

import requests
import scrapy
from ..items import XinLang_CheXing
import time
from scrapy.conf import settings

website = 'xinlang_chexing'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = "https://data.auto.sina.com.cn/api/shengliang/getSerialTop/"
    second_url = "https://data.auto.sina.com.cn/api/shengliang/getSerialTop/{}/{}/2/"
    year_url = "https://data.auto.sina.com.cn/api/shengliang/getDateList/2/"
    type_list = ["总榜", "轿车", "SUV", "MPV", "新能源", ]
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
        year_dict = requests.get(url=self.year_url, headers=self.headers).json()["data"]
        return year_dict

    def start_requests(self):
        year_list = self.get_year()
        meta = {"endDay": "",
                "startDay": "",
                "week": "",
                "year": "", }
        yield scrapy.Request(url=self.start_urls, headers=self.headers, meta=meta)
        # for year in year_list[0:1]:
        #     # print(year)
        #     meta = {"endDay": year["endDay"],
        #             "startDay": year["startDay"],
        #             "week": year["week"],
        #             "year": year["year"], }
        #     url = self.second_url.format(year["year"], year["week"])
        #     yield scrapy.Request(url=url, headers=self.headers, meta=meta)

    def get_zhishu(self, num):
        url = "https://data.auto.sina.com.cn/api/shengliang/getSldaylist/{}/1/".format(num)
        data = requests.get(url=url, headers=self.headers).json()["data"][num]
        return data

    def parse(self, response):
        koubei_all_list = json.loads(response.body)["data"]
        for koubei_list in koubei_all_list:
            level = koubei_list
            for koubei in koubei_all_list[koubei_list]:
                item = XinLang_CheXing()
                item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item["url"] = response.url
                item["rank"] = koubei_all_list[koubei_list][koubei]["rank"]
                item["slvalue"] = koubei_all_list[koubei_list][koubei]["slvalue"]
                item["serialId"] = koubei_all_list[koubei_list][koubei]["serialId"]
                item["serialName"] = koubei_all_list[koubei_list][koubei]["serialName"]
                item["pic"] = koubei_all_list[koubei_list][koubei]["pic"]
                item["whitePic"] = koubei_all_list[koubei_list][koubei]["whitePic"]
                item["preSlvalue"] = koubei_all_list[koubei_list][koubei]["preSlvalue"]
                item["changeSign"] = koubei_all_list[koubei_list][koubei]["changeSign"]
                item["changeValue"] = koubei_all_list[koubei_list][koubei]["changeValue"]
                item["level"] = level
                item["zhishu"] = str(self.get_zhishu(item["serialId"]))
                item["statusplus"] = str(koubei_all_list[koubei_list][koubei]) + level+str(1)+str(item["year"])+str(item["week"])
                item["endDay"] = response.meta["endDay"]
                item["startDay"] = response.meta["startDay"]
                item["week"] = response.meta["week"]
                item["year"] = response.meta["year"]
                yield  item
                # print(item)
