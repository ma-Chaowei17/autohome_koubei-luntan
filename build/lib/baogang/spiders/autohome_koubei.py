# # -*- coding: utf-8 -*-
# import requests
# import scrapy
# from lxml import etree
# from lxml.etree import HTML
#
# from ..deal_font import fontConvert
# from ..proxy import get_ug
# from ..items import Autohome_koubei_all
# import time
# from scrapy.conf import settings
# import logging
# import re
# from scrapy_splash import SplashRequest
#
# website = 'autohome_koubei1'
#
# # scrapy crawl autohome_koubei1
# class CarSpider(scrapy.Spider):
#     name = website
#     start_urls = "https://k.autohome.com.cn/detail/view_01dst85gna68w38d1g6wv00000.html?st=4&piap=0%7C3170%7C0%7C0%7C2%7C0%7C0%7C0%7C0%7C0%7C3#pvareaid=2112108"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
#         "Referer": "https://www.autohome.com.cn"
#     }
#     custom_settings = {
#         "SPLASH_URL": "http://192.168.1.172:8050/",
#         "HTTPCACHE_STORAGE": 'scrapy_splash.SplashAwareFSCacheStorage',
#         "SPIDER_MIDDLEWARES": {'scrapy_splash.SplashDeduplicateArgsMiddleware': 100},
#         "DUPEFILTER_CLASS": 'scrapy_splash.SplashAwareDupeFilter',
#         "DOWNLOADER_MIDDLEWARES": {
#             'baogang.proxy.AutohomeProxyMiddleware': 850,
#             'scrapy_splash.SplashCookiesMiddleware': 723,
#             'scrapy_splash.SplashMiddleware': 725,
#             'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
#
#         },
#         "CONCURRENT_REQUESTS":6,
#         "DEFAULT_REQUEST_HEADERS": {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#         }
#     }
#
#     def __init__(self, **kwargs):
#         super(CarSpider, self).__init__(**kwargs)
#         self.counts = 0
#         self.carnum = 800000
#         settings.set("WEBSITE", website, priority='cmdline')
#         settings.set('CrawlCar_Num', self.carnum, priority='cmdline')
#         settings.set('MYSQLDB_DB', 'baogang', priority='cmdline')
#
#     def start_requests(self):
#         yield SplashRequest(url=self.start_urls, headers=self.headers, args={'wait': 1}, callback=self.parse)
#
#     def deal_ttf(self, url):
#         User_Agent = {'User-Agent': get_ug()}
#         try:
#             text = requests.get(url=url, headers=User_Agent)
#         except:
#             logging.log(msg='Proxy request timeout Wait for two seconds', level=logging.INFO)
#             return 0
#         else:
#             # window
#             with open("./text_dazhong1.ttf", "bw")as f:
#                 # linux
#                 # with open("/home/home/mywork/font/luntan/text_baogang.ttf", "bw")as f:
#                 f.write(text.content)
#         # window
#         return fontConvert("./text_dazhong1.ttf")
#         # linux
#         # return fontConvert("/home/home/mywork/font/luntan/text_baogang.ttf")
#
#     def parse(self, response):
#         ttf_text_url = "https:" + re.findall(r" url\('(.*)'\) format\('woff'\)", response.text)[0]
#         font_dict = self.deal_ttf(ttf_text_url)
#         content = re.sub(r"<style (.*?)</style>", "", response.text)
#         content = re.sub(r"<script(.*?)</script>", "", content)
#         html = HTML(content)
#         content = html.xpath("string(//div[@class='text-con'])")
#         new_content = ''
#         for i in content:
#             try:
#                 new_content = new_content + font_dict[i]
#             except:
#                 new_content = new_content + i
#         print(new_content)
