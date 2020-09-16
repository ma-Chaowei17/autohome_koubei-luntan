# -*- coding: utf-8 -*-
import re
import time
from ..items import lianjia

import scrapy
from scrapy.conf import settings

# 爬虫名
website = "lianjia_house"


class AutohomeSpider(scrapy.Spider):
    name = website

    custom_settings = {
        "DOWNLOAD_DELAY": 0,
        "CONCURRENT_REQUESTS": 16,
        'RETRY_TIMES': 6

    }

    # 做一些配置的操作
    def __init__(self, **kwargs):
        super(AutohomeSpider, self).__init__(**kwargs)
        self.counts = 0
        self.carnum = 20000000
        self.start_urls = {'https://bj.lianjia.com/ershoufang/': '北京',
                           'https://gz.lianjia.com/ershoufang': '广州', 'https://sz.lianjia.com/ershoufang': '深圳',
                           'https://tj.lianjia.com/ershoufang/': "天津", "https://sh.lianjia.com/ershoufang/": '上海', }
        self.city_dict = {'北京': 'https://bj.lianjia.com', '上海': 'https://sh.lianjia.com',
                          '广州': 'https://gz.lianjia.com', '深圳': 'https://sz.lianjia.com',
                          '天津': 'https://tj.lianjia.com'
                          }

        settings.set("WEBSITE", website, priority='cmdline')
        settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQL_SERVER', '192.168.1.94', priority='cmdline')
        settings.set('MYSQLDB_PASS', '94dataUser@2020', priority='cmdline')
        settings.set('MYSQLDB_DB', 'koubei', priority='cmdline')
        settings.set('MYSQLDB_USER', 'dataUser94', priority='cmdline')

    def start_requests(self):
        for i in self.start_urls:
            headers = {'Referer': i,
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
            yield scrapy.Request(url=i,
                                 headers=headers,
                                 meta={'city_aa': i}
                                 )

    #     需要特别处理的内容  车家号url中包含chejiahao      汽车之家autohome 今日头条 toutiao
    def parse(self, response):
        url_list = response.xpath("//div[@data-role='ershoufang']/div[last()]/a/@href").extract()
        city_list = response.xpath("//div[@data-role='ershoufang']/div[last()]/a/text()").extract()
        city_dict = dict(zip(url_list, city_list, ))
        for i in city_dict:
            url = self.city_dict[self.start_urls[response.meta['city_aa']]]+ i
            meta = {
                'area': city_dict[i],
                'big_area': self.start_urls[response.meta['city_aa']]
            }
            response.meta.update(meta)
            headers = {'Referer': response.meta['city_aa'],
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
            yield scrapy.Request(url=url, meta=response.meta, headers=headers, callback=self.samll_area)

    def samll_area(self, response):
        url_list = response.xpath("//div[@data-role='ershoufang']/div[last()]/a/@href").extract()
        city_list = response.xpath("//div[@data-role='ershoufang']/div[last()]/a/text()").extract()
        city_dict = dict(zip(url_list, city_list, ))
        for i in city_dict:
            url = self.city_dict[self.start_urls[response.meta['city_aa']]]+ i
            meta = {
                'small_area': city_dict[i],
                'page': 1,
                'first_url': ""
            }
            response.meta.update(meta)
            headers = {'Referer':response.meta['city_aa'],
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
            yield scrapy.Request(url=url, meta=response.meta, headers=headers, callback=self.city_deal)

    def city_deal(self, response):
        first_used_url = response.xpath("//ul[@log-mod='list']/li[1]//div[@class='title']/a/@href").extract_first()
        data_list = response.xpath("//ul[@log-mod='list']/li")
        if first_used_url == response.meta["first_url"]:
            return
        else:
            response.meta["first_url"] = first_used_url
        for data in data_list:
            item = lianjia()
            item["small_area"] = response.meta["small_area"]
            item["area"] = response.meta["area"]
            item["big_area"] = response.meta["big_area"]
            item["url"] = data.xpath(".//div[@class='title']/a/@href").extract_first()
            item["price"] = data.xpath(".//div[@class='totalPrice']/span/text()").extract_first()
            item["title"] = data.xpath(".//div[@class='title']/a/text()").extract_first().strip()
            item["address"] = "-".join(data.xpath(".//div[@class='positionInfo']/a/text()").extract())
            item["desc"] = data.xpath(".//div[@class='houseInfo']/text()").extract_first().strip("")
            item["unit_price"] = data.xpath(".//div[@class='unitPrice']/span/text()").extract_first().strip("")
            item["posted_time"] = data.xpath(".//div[@class='followInfo']/text()").extract_first().split('/')[1]
            item["grad_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item["statusplus"] = item["url"] + (str(1511))
            # print(item)
            yield item
        # // f翻页
        response.meta['page'] = response.meta['page'] + 1
        if response.meta['page'] == 2:
            next_url = response.url + "pg{}".format(response.meta['page'])
        else:
            # print( re.sub('pg(\d+)', 'pg888',"ssssss/pg55",))
            next_url = re.sub('pg(\d+?)', 'pg{}'.format(response.meta["page"]), response.url)
        headers = {'Referer': response.meta['city_aa'],
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        yield scrapy.Request(url=next_url, meta=response.meta, callback=self.city_deal, headers=headers)
