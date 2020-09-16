import json
import logging
import re

import requests
import scrapy
from ..items import xinlang_pingfen
import time
from scrapy.conf import settings

website = 'xinlang_pingfen'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = "https://price.auto.sina.cn/api/salesApi/getHasSaleBrands"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://auto.sina.com.cn"
    }

    custom_settings = {
        # "DOWNLOADER_MIDDLEWARES": {
        # },
        "DOWNLOAD_DELAY": 0.3
    }

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 800000
        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'baogang', priority='cmdline')
        self.type_dict = {
            "1": "外观",
            "2": "操控",
            "3": "动力",
            "4": "油耗",
            "5": "舒适",
            "6": "空间",
            "7": "内饰",
            "8": "性价比",

        }

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers, )

    def parse(self, response):
        brand_dict = json.loads(response.text)["data"]
        for i in brand_dict:
            # print(brand_dict[i])
            if i == 'a' :
                for x in brand_dict[i]:
                    print(x)
                    meta = {
                        "zhName": x["zhName"],
                        "brandid": x['id']
                    }
                    url = "https://db.auto.sina.cn/api/car/getBrandDetail.json?brandid={}".format(
                        meta["brandid"])
                    yield scrapy.Request(url=url, headers=self.headers, meta=meta, callback=self.series_prase)

            else:
                for x in brand_dict[i]:
                    print(x)
                    meta = {
                        "zhName": brand_dict[i][x]["zhName"],
                        "brandid": brand_dict[i][x]['id']
                    }

                    url = "https://db.auto.sina.cn/api/car/getBrandDetail.json?brandid={}".format(
                        meta["brandid"])
                    yield scrapy.Request(url=url, headers=self.headers, meta=meta, callback=self.series_prase)

    def series_prase(self, response):
        series_dict = json.loads(response.text)["result"]["data"]["data_list"]
        for i in series_dict:
            for data in series_dict[i]["data_list"]["data"]:
                meta = {
                    "id": data["serialId"],
                    "Car_name": data["cname"],

                }
                url = "https://price.auto.sina.cn/api/paihangbang/getCommentBySub?subid={}".format(meta["id"])

                response.meta.update(meta)
                yield scrapy.Request(url=url, headers=self.headers, meta=response.meta,
                                     callback=self.car_parse)

    def car_parse(self, response):
        try:
            data = json.loads(response.text)["data"]["score_info"]["sub_info"]
        except:
            item = xinlang_pingfen()
            item["grade_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["url"] = response.url
            item["statusplus"] = response.url
            item["brand"] = response.meta["zhName"]
            item["car_series"] = response.meta['Car_name']
            item["car_model"] = ""
            item["total_score"] = ""
            item["space"] = ""
            item["power"] = ""
            item["manipulation"] = ""
            item["fuel_consumption"] = ""
            item["comfortability"] = ""
            item["appearance"] = ""
            item["interior_trim"] = ""
            item["cost_performance"] = ""
            item["car_space"] = ""
            item["car_power"] = ""
            item["car_manipulation"] = ""
            item["car_fuel_consumption"] = ""
            item["car_comfortability"] = ""
            item["car_appearance"] = ""
            item["car_interior_trim"] = ""
            item["car_cost_performance"] = ""
            item["user"] = ""
            yield item
        else:

            car_dict = {}
            car_dict["grade_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            car_dict["brand"] = response.meta["zhName"]
            car_dict["car_series"] = response.meta['Car_name']
            car_dict["total_score"] = data["sum_score"]
            car_dict["space"] = data["space_score"]
            car_dict["power"] = data["power_scoure"]
            car_dict["manipulation"] = data["control_score"]
            car_dict["fuel_consumption"] = data["fuel_consumption_score"]
            car_dict["comfortability"] = data["comfort_score"]
            car_dict["appearance"] = data["exterior_score"]
            car_dict["interior_trim"] = data["interior_score"]
            car_dict["cost_performance"] = data["cost_performance_score"]
            car_dict["url"] = response.url
            for i in range(8):
                url = "https://price.auto.sina.cn/api/paihangbang/getCommentByPage?subid={}&type={}&page=1".format(
                    response.meta["id"], i + 1)
                yield scrapy.Request(url, meta={"meta": response.meta, "item": car_dict, "page": 1, "type": i + 1},
                                     callback=self.user_parse)
        # url = "https://price.auto.sina.cn/api/paihangbang/getCommentByPage?subid={}&type={}&page=1".format(
        #                     response.meta["meta]["id"], response.meta["type"],response.meta["page"])

    def user_parse(self, response):
        print(response.meta)
        type = str(re.findall("&type=(\d+)&", response.url)[0])
        response.meta["page"] = response.meta["page"] + 1
        data = json.loads(response.text)["data"]
        if data == []:
            item = xinlang_pingfen()
            item["grade_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["url"] = response.url
            item["brand"] = response.meta["meta"]["zhName"]
            item["car_series"] = response.meta["meta"]['Car_name']
            item["total_score"] = response.meta["item"]["total_score"]
            item["space"] = response.meta["item"]["space"]
            item["power"] = response.meta["item"]["power"]
            item["manipulation"] = response.meta["item"]["manipulation"]
            item["fuel_consumption"] = response.meta["item"]["fuel_consumption"]
            item["comfortability"] = response.meta["item"]["comfortability"]
            item["appearance"] = response.meta["item"]["appearance"]
            item["interior_trim"] = response.meta["item"]["interior_trim"]
            item["cost_performance"] = response.meta["item"]["cost_performance"]
            item["car_model"] = ""
            item["car_space"] = ""
            item["car_power"] = ""
            item["car_manipulation"] = ""
            item["car_fuel_consumption"] = ""
            item["car_comfortability"] = ""
            item["car_appearance"] = ""
            item["car_interior_trim"] = ""
            item["car_cost_performance"] = ""
            item["user"] = ""
            item["statusplus"] = response.url
            # print(item)
            yield item
        else:
            for car in data:
                item = xinlang_pingfen()
                item["grade_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item["url"] = response.url
                item["brand"] = response.meta["meta"]["zhName"]
                item["car_series"] = response.meta["meta"]['Car_name']
                item["total_score"] = response.meta["item"]["total_score"]
                item["space"] = response.meta["item"]["space"]
                item["power"] = response.meta["item"]["power"]
                item["manipulation"] = response.meta["item"]["manipulation"]
                item["fuel_consumption"] = response.meta["item"]["fuel_consumption"]
                item["comfortability"] = response.meta["item"]["comfortability"]
                item["appearance"] = response.meta["item"]["appearance"]
                item["interior_trim"] = response.meta["item"]["interior_trim"]
                item["cost_performance"] = response.meta["item"]["cost_performance"]
                item["car_model"] = car["sina_car_name"]
                item["user"] = car["sina_uname"]
                # car["score"]
                # self.type_dict = {
                #     "1": "外观",
                #     "2": "操控",
                #     "3": "动力",
                #     "4": "油耗",
                #     "5": "舒适",
                #     "6": "空间",
                #     "7": "内饰",
                #     "8": "性价比",
                #
                # }
                if type == "1":
                    item["car_space"] = ""
                    item["car_power"] = ""
                    item["car_manipulation"] = ""
                    item["car_fuel_consumption"] = ""
                    item["car_comfortability"] = ""
                    item["car_appearance"] = car["score"]
                    item["car_interior_trim"] = ""
                    item["car_cost_performance"] = ""
                if type == "2":
                    item["car_space"] = ""
                    item["car_power"] = ""
                    item["car_manipulation"] = car["score"]
                    item["car_fuel_consumption"] = ""
                    item["car_comfortability"] = ""
                    item["car_appearance"] = ""
                    item["car_interior_trim"] = ""
                    item["car_cost_performance"] = ""
                if type == "3":
                    item["car_space"] = ""
                    item["car_power"] = car["score"]
                    item["car_manipulation"] = ""
                    item["car_fuel_consumption"] = ""
                    item["car_comfortability"] = ""
                    item["car_appearance"] = ""
                    item["car_interior_trim"] = ""
                    item["car_cost_performance"] = ""
                if type == "4":
                    item["car_space"] = ""
                    item["car_power"] = ""
                    item["car_manipulation"] = ""
                    item["car_fuel_consumption"] = car["score"]
                    item["car_comfortability"] = ""
                    item["car_appearance"] = ""
                    item["car_interior_trim"] = ""
                    item["car_cost_performance"] = ""
                if type == "5":
                    item["car_space"] = ""
                    item["car_power"] = ""
                    item["car_manipulation"] = ""
                    item["car_fuel_consumption"] = ""
                    item["car_comfortability"] = car["score"]
                    item["car_appearance"] = ""
                    item["car_interior_trim"] = ""
                    item["car_cost_performance"] = ""
                if type == "6":
                    item["car_space"] = car["score"]
                    item["car_power"] = ""
                    item["car_manipulation"] = ""
                    item["car_fuel_consumption"] = ""
                    item["car_comfortability"] = ""
                    item["car_appearance"] = ""
                    item["car_interior_trim"] = ""
                    item["car_cost_performance"] = ""
                if type == "7":
                    item["car_space"] = ""
                    item["car_power"] = ""
                    item["car_manipulation"] = ""
                    item["car_fuel_consumption"] = ""
                    item["car_comfortability"] = ""
                    item["car_appearance"] = ""
                    item["car_interior_trim"] = car["score"]
                    item["car_cost_performance"] = ""
                if type == "8":
                    item["car_space"] = ""
                    item["car_power"] = ""
                    item["car_manipulation"] = ""
                    item["car_fuel_consumption"] = ""
                    item["car_comfortability"] = ""
                    item["car_appearance"] = ""
                    item["car_interior_trim"] = ""
                    item["car_cost_performance"] = car["score"]
                item["statusplus"] = response.url + str(item["user"]) + str(item["car_model"]) + str(
                    item["car_cost_performance"]) + str(item["car_interior_trim"]) + str(item["car_appearance"]) + str(
                    item["car_comfortability"]) + str(item["car_space"]) + str(item["car_power"]) + str(
                    item["car_manipulation"]) + str(item["car_fuel_consumption"])
                # print(item)
                yield item
            url = "https://price.auto.sina.cn/api/paihangbang/getCommentByPage?subid={}&type={}&page={}".format(
                response.meta["meta"]["id"], response.meta["type"], response.meta["page"])
            yield scrapy.Request(url, meta=response.meta,
                                 callback=self.user_parse)
