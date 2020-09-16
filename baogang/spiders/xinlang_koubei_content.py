import json
import logging

import requests
import scrapy
from ..items import xinlang_koubei_content
import time
from scrapy.conf import settings

website = 'xinlang_koubei_content'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = "https://price.auto.sina.cn/api/salesApi/getHasSaleBrands"
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
        yield scrapy.Request(url=self.start_urls, headers=self.headers, )

    def parse(self, response):
        brand_dict = json.loads(response.text)["data"]
        for i in brand_dict:
            # print(brand_dict[i])
            if i == 'a':
                for x in brand_dict[i]:
                    meta = {
                        "zhName": x["zhName"],
                        "brandid": x['id']
                    }
                    url = "https://db.auto.sina.com.cn/api/cms/car/getSerialList.json?brandid={}".format(
                        meta["brandid"])
                    yield scrapy.Request(url=url, headers=self.headers, meta=meta, callback=self.series_prase)

            else:
                # return
                for x in brand_dict[i]:
                    meta = {
                        "zhName": brand_dict[i][x]["zhName"],
                        "brandid": brand_dict[i][x]['id']
                    }

                    url = "https://db.auto.sina.com.cn/api/cms/car/getSerialList.json?brandid={}".format(
                        meta["brandid"])
                    yield scrapy.Request(url=url, headers=self.headers, meta=meta, callback=self.series_prase)

    #                     url ="http://data.auto.sina.com.cn/car_comment/list_626_0.html"
    def get_fenxi(self, id):
        url = "https://data.auto.sina.com.cn/car/api/auto/get_buy_intent.php?subid={}".format(id)
        text = requests.get(url=url, headers=self.headers).text
        return text

    def series_prase(self, response):
        series_dict = json.loads(response.text)["data"]
        for i in series_dict:
            corpId = i["corpId"]
            corpName = i["corpName"]
            for x in i["serialList"]:
                fenxi = self.get_fenxi(x["serialId"])
                meta = {
                    "fenxi": fenxi,
                    "serialName": x["serialName"],
                    "serialLevel": x["serialLevel"],
                    "sellStatus": x["sellStatus"],
                    "serialId": x["serialId"],
                    "autoType": x["autoType"],
                    "guidePrice": x["guidePrice"],
                    "corpId": corpId,
                    "corpName": corpName,
                }
                # print(meta)
                url = "http://data.auto.sina.com.cn/car_comment/list_{}_0.html".format(meta["serialId"])
                response.meta.update(meta)
                yield scrapy.Request(url=url, headers=self.headers, meta=response.meta,
                                     callback=self.car_parse)

    def deal_time(self, deal_time):
        # 一年 = 31536081
        a1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # print(a1)
        a2 = deal_time
        timeArray1 = time.strptime(a1, "%Y-%m-%d %H:%M:%S")
        timeArray2 = time.strptime(a2, "%Y-%m-%d %H:%M:%S")
        timeStamp1 = int(time.mktime(timeArray1))
        timeStamp2 = int(time.mktime(timeArray2))
        logging.log(msg=(timeStamp1, "*" * 50, timeStamp2), level=logging.INFO)
        index = timeStamp1 - timeStamp2
        if index <= 31536081:
            return True
        else:
            return False

    def car_parse(self, response):
        next_page = response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
        if next_page == None:
            return
        else:
            url = next_page
            yield scrapy.Request(url=url, headers=self.headers, meta=response.meta,
                                 callback=self.car_parse)
        koubei_list = response.xpath("//div[@class='wpkwp_ck']/dl")
        try:
            koubei_bang = str(dict(
                zip(response.xpath("//div[@class='box-bd']//li//div[@class='fL']/a/text()").extract()[0:5],
                    response.xpath("//div[@class='box-bd']//li//div[@class='fR']/span[1]/text())").extract()[0:5])))
        except:
            koubei_bang = "{}"
        # print(koubei_bang)
        for koubei in koubei_list:
            koubei_url = koubei.xpath(".//span[@class='fL']/a/@href").extract_first()
            reply_num = koubei.xpath(".//em[@class='replay01']/i/text()").extract_first().strip("(").strip(")")
            support_num = koubei.xpath(".//em[@class='ding01']//i/b/text()").extract_first()
            postedtime = koubei.xpath(".//p[@class='ms']/span[@class='fL']/text()").extract_first()
            # print(postedtime)
            index = self.deal_time(postedtime)
            # print(index)
            if index:
                meta = {
                    "koubei_bang": koubei_bang,
                    "support_num": support_num,
                    "reply_num": reply_num,
                    "postedtime": postedtime
                }
                response.meta.update(meta)
                yield scrapy.Request(url=koubei_url, headers=self.headers, meta=response.meta,
                                     callback=self.tent_parse)
            else:
                continue

    def tent_parse(self, response):
        item = xinlang_koubei_content()
        item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["url"] = response.url
        item["koubei_bang"] = response.meta["koubei_bang"]
        item["zhName"] = response.meta["zhName"]
        item["zhName"] = response.meta["zhName"]
        item["fenxi"] = response.meta["fenxi"]
        item["serialName"] = response.meta["serialName"]
        item["serialLevel"] = response.meta["serialLevel"]
        item["sellStatus"] = response.meta["sellStatus"]
        item["serialId"] = response.meta["serialId"]
        item["autoType"] = response.meta["autoType"]
        item["guidePrice"] = response.meta["guidePrice"]
        item["corpId"] = response.meta["corpId"]
        item["corpName"] = response.meta["corpName"]
        item["support_num"] = response.meta["support_num"]
        item["reply_num"] = response.meta["reply_num"]
        item["postedtime"] = response.meta["postedtime"]
        content = response.xpath("//p[@class='zs']")
        item["content"] = content.xpath("string(.)").extract()
        item["title"] = response.xpath("//p[@class='ti']//a[@class='fL']/text()").extract_first()
        item["statusplus"] = response.text
        # print(item)
        yield item
