# https://www.autohome.com.cn/car/


import json
import re

import requests
import scrapy
from ..items import Autohome_pingfen_for_home
import time
from scrapy.conf import settings

website = 'telaidian'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = ["https://www.autohome.com.cn/car/"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.4.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat"
        , "Referer": "https://servicewechat.com/wx8d32c1a71ecd965d/153/page-frame.html"
        , 'TELDAppID': "",
        'Host': 'sgi.teld.cn'
    }
    index = True
    custom_settings = {
        # "DOWNLOADER_MIDDLEWARES": {
        # },
        "DOWNLOAD_DELAY": 1
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 800000
        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQL_SERVER', '192.168.1.94', priority='cmdline')
        settings.set('MYSQLDB_PASS', '94dataUser@2020', priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQLDB_USER', 'dataUser94', priority='cmdline')

    def start_requests(self):
        url = 'https://sgi.teld.cn/api/invoke?SID=AAS-App0407_SearchStation&ELDAppID%3d%26param%3d%7b%22pageNum%22%3a1%2c%22itemNumPerPage%22%3a20%2c%22locationFilterType%22%3a%221%22%2c%22lng%22%3a121.27855345898439%2c%22lat%22%3a31.099815089030958%2c%22sortType%22%3a%221%22%2c%22coordinateType%22%3a%22gaode%22%2c%22keyword%22%3a%22%22%2c%22rideShareTag%22%3a%22%22%2c%22locationFilterValue%22%3a200%2c%22myCollectFirst%22%3a1%7d%26X-Token%3dC01eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiIiLCJzZXNzaW9uX2lkIjoiIiwidG9rZW5faWQiOiI4NjExMTE4Y2YyYzA0YjBmODI3N2RiZWRjYjMzMDFkMyIsInJlZnJlc2h0b2tlbl9pZCI6IjFiZDYzYjdlYjJlNDQxNjhhYWM3MzUwYTBkZGNkZGQwIiwidmFsaWRhdGVfdHlwZSI6MSwic2NvcGUiOiIqIiwic291cmNlIjoiQyIsImRldl9pZCI6IjlkODQwODAzLTg4MWItMGYyOS1kZjEyLWQzNDg0NWU1ZDM2NiIsImV4cCI6MTU4NzcwNzU5Ny4wLCJjcmVhdGVfZnJvbSI6InNldCIsInJkc19mbGFnIjoxfQ.W3tNP3xcB_C2-a2yjkqligtcXUtYs5eRHXUj_cyygGM%26STS%3d1587706397%26SVER%3dMMLQxKDBreiHqVGsio7%2fMA%3d%3d%26SSDI%3d9d840803-881b-0f29-df12-d34845e5d366%26SCOI%3d%26SCOL%3d%26SRS%3dSP'

        yield scrapy.Request(method='GET',url=url,  headers=self.headers, )

    def parse(self, response):
        print(json.loads(response.text))

    def parse_next_page(self, response):
        if "specState" not in response.url:
            data_list = response.xpath("//ul[@id='specListUL']/li")
            if len(data_list) <= 2:
                return
            for data in data_list[1::]:
                meta = {}
                meta["id"] = re.findall(r"/(\d+)/", data.xpath(".//div[@class='emiss-title']/a/@href").extract_first())[
                    0]
                meta["brand"] = response.meta["brand"]
                meta["car_series"] = response.meta["series"]
                meta["car_model"] = data.xpath(".//div[@class='emiss-title']/a/text()").extract_first().strip()
                meta["total_score"] = data.xpath(".//div[@class='emiss-fen']/text()").extract_first().strip()
                url = "https://k.autohome.com.cn/spec/{}/".format(meta["id"])
                yield scrapy.Request(url=url, headers=self.headers, meta=meta,
                                     callback=self.car_prase)
        else:
            data_list = json.loads(response.text)
            for data in data_list:
                meta = {}
                meta["id"] = data["SpecId"]
                meta["brand"] = response.meta["brand"]
                meta["car_series"] = response.meta["series"]
                meta["car_model"] = data["SpecName"]
                meta["total_score"] = data["Average"]
                url = "https://k.autohome.com.cn/spec/{}/".format(meta["id"])
                yield scrapy.Request(url=url, headers=self.headers, meta=meta,
                                     callback=self.car_prase)

    def car_prase(self, response):
        item = Autohome_pingfen_for_home()
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # https://k.autohome.com.cn/spec/10231/
        item["autohomeid"] = re.findall(r"/spec/(\d+)/", response.url)[0]
        item["brand"] = response.meta["brand"]
        item["car_series"] = response.meta["car_series"]
        item["car_model"] = response.meta["car_model"]
        item["total_score"] = response.meta["total_score"]
        item["space"] = response.xpath("//div[contains(text(),'空间')]/../div[2]/text()").extract_first().strip()
        item["power"] = response.xpath("//div[contains(text(),'动力')]/../div[2]/text()").extract_first().strip()
        item["manipulation"] = response.xpath("//div[contains(text(),'操控')]/../div[2]/text()").extract_first().strip()
        try:
            item["fuel_consumption"] = response.xpath(
                "//div[contains(text(),'油耗')]/../div[2]/text()").extract_first().strip()
        except:
            item["fuel_consumption"] = response.xpath(
                "//div[contains(text(),'电耗')]/../div[2]/text()").extract_first().strip()
        item["comfortability"] = response.xpath(
            "//div[contains(text(),'舒适性')]/../div[2]/text()").extract_first().strip()
        item["appearance"] = response.xpath("//div[contains(text(),'外观')]/../div[2]/text()").extract_first().strip()
        item["interior_trim"] = response.xpath("//div[contains(text(),'内饰')]/../div[2]/text()").extract_first().strip()
        item["cost_performance"] = response.xpath(
            "//div[contains(text(),'性价比')]/../div[2]/text()").extract_first().strip()
        item["url"] = response.url
        item["statusplus"] = response.url + str(
            item["space"]) + str(item["power"]) + str(item[
                                                          "manipulation"]) + str(item["fuel_consumption"]) + str(
            item["comfortability"]) + str(item["appearance"]) + str(item[
                                                                        "interior_trim"]) + str(
            item["cost_performance"]) + str(1112222)
        url = "https://dealer.api.autohome.com.cn/dealerrest/price/GetMinPriceBySpecSimple?specids={}&_appId=cms".format(
            item["autohomeid"])

        yield scrapy.Request(url=url, meta={"item": item}, headers=self.headers, callback=self.deal_prcie)

    def deal_prcie(self, response):
        # print(response.url)
        text = json.loads(response.text)["result"]["list"]
        item = response.meta["item"]
        try:
            item["dealer_price"] = text[0]["MinPrice"]
            print(item["dealer_price"])
        except:
            item["dealer_price"] = None
        yield item
