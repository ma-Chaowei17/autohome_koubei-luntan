# https://www.autohome.com.cn/car/


import json
import re

import requests
import scrapy
from ..items import Autohome_pingfen_for_home
import time
from scrapy.conf import settings

website = 'autohome_pingfen_for_home'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = ["https://www.autohome.com.cn/car/"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.autohome.com.cn"
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

    def add_url(self):
        url = "https://www.autohome.com.cn/grade/carhtml/{}.html"
        car_list = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
                    "V", "W ", "X", "Y", "Z"]
        for i in car_list:
            self.start_urls.append(url.format(i))

    def start_requests(self):
        self.add_url()
        for i in self.start_urls:
            yield scrapy.Request(url=i, headers=self.headers, )
        # yield scrapy.Request(url=self.start_urls[0], headers=self.headers, )

    def parse(self, response):
        if response.url == "https://www.autohome.com.cn/car/":
            brand_list = response.xpath("//div[@id='htmlA']//dl")
        else:
            brand_list = response.xpath("//dl")

        for i in brand_list:
            brand = i.xpath(".//dt//div//a/text()").extract_first()
            for x in i.xpath(".//dd//div[@class='h3-tit']"):
                factory = x.xpath(".//text()").extract_first()
                for a in x.xpath(".//following-sibling::ul[1]//li"):
                    series = a.xpath(".//h4/a/text()").extract_first()
                    url = a.xpath(".//div//a[contains(text(),'口碑')]/@href").extract_first()
                    if url == None:
                        continue
                    serier_id = re.findall(r"cn/(\d*)/", url)[0]

                    meta = {
                        "brand": brand,
                        "factory": factory,
                        "series": series,
                        "serier_id": serier_id
                    }
                    url = []
                    url.append(
                        "https://k.autohome.com.cn/FrontAPI/GetSpecListBySeriesId?seriesId={}&specState=1".format(
                            serier_id))
                    url.append("https://k.autohome.com.cn/{}/".format(serier_id))
                    url.append("https://k.autohome.com.cn/{}/stopselling/".format(serier_id))
                    url.append(
                        "https://k.autohome.com.cn/FrontAPI/GetSpecListBySeriesId?seriesId={}&specState=3".format(
                            serier_id))
                    for i in url:
                        yield scrapy.Request(url=i, headers=self.headers, meta=meta,
                                             callback=self.parse_next_page)

    def parse_next_page(self, response):
        if "specState" not in response.url:
            data_list = response.xpath("//ul[@id='specListUL']/li")
            if len(data_list) <=2:
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
        item["autohomeid"] =re.findall(r"/spec/(\d+)/",response.url)[0]
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
            item["cost_performance"])+str(1112222)
        url ="https://dealer.api.autohome.com.cn/dealerrest/price/GetMinPriceBySpecSimple?specids={}&_appId=cms".format(item["autohomeid"])

        yield scrapy.Request(url=url,meta={"item":item},headers=self.headers,callback=self.deal_prcie)

    def deal_prcie(self,response):
        # print(response.url)
        text =json.loads(response.text)["result"]["list"]
        item =response.meta["item"]
        try:
            item["dealer_price"] =text[0]["MinPrice"]
            print(item["dealer_price"])
        except:
            item["dealer_price"] = None
        yield item

