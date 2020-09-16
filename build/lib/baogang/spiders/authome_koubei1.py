# -*- coding: utf-8 -*-
import scrapy
from ..items import Autohome_koubei_all
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from ..koubei_font import get_map
from ..proxy import get_ug
from ..items import Autohome_koubei_all
import time
from scrapy.conf import settings
import logging
import re, os.path
from scrapy_splash import SplashRequest

website = 'kang_autohome_koubei'


class CarSpider(scrapy.Spider):
    name = website
    # https://data.auto.sina.com.cn/api/shengliang/getDateList/2/ 实时
    start_urls = ["https://www.autohome.com.cn/car/"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.autohome.com.cn"
    }
    custom_settings = {

        "DEFAULT_REQUEST_HEADERS": {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        'RETRY_ENABLED': 3,
        "CONCURRENT_REQUESTS": 1
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

        chrome_opts = Options()
        chrome_opts.add_argument('--headless')
        chrome_opts.add_argument('--disable-images')
        chrome_opts.add_argument('--incognito')  #  无痕模式
        chrome_opts.add_argument('--start-maximized')
        chrome_opts.add_argument('--no-sandbox')
        chrome_opts.add_argument('--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"')
        chrome_opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_opts)

    def __del__(self):
        self.driver.close()

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

    def parse(self, response):
        car_list = [
            '途观L新能源', "探岳GTE插电混动", "唐新能源", "宋Pro新能源", "荣威RX5新能源", "宝马X1新能源",
            "帕萨特新能源", "迈腾", "雷凌双擎E+", "汉", "雅阁", "凯美瑞",
        ]
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
                    # print(url)
                    # href="//k.autohome.com.cn/4526/#pvareaid=103459"
                    if url == None:
                        continue
                    serier_id = re.findall(r"cn/(\d*)/", url)[0]

                    meta = {
                        "brand": brand,
                        "factory": factory,
                        "series": series,
                        "serier_id": serier_id
                    }
                    if series in car_list:
                        yield scrapy.Request(url='https:' + url, headers=self.headers, meta=meta,
                                             callback=self.parse_next_page)


    def parse_next_page(self, response):
        # print(response.url)
        next_page_url = response.xpath("//div[@class='page']/a[contains(text(),'下一页')]/@href").extract_first()
        bad_msg = str(response.xpath("//a[@class=' dust']/text()").extract())
        print(next_page_url, "*x" * 50)
        if next_page_url == None:
            return
        else:
            yield response.follow(url=next_page_url, headers=self.headers, meta=response.meta,
                                  callback=self.parse_next_page)
        # 解析时间
        koubei_list = response.xpath("//div[@class='mouthcon']")
        for koubei in koubei_list:
            posted_time = koubei.xpath(
                ".//div[@class='title-name name-width-01']/b//a[1]/text()").extract_first() + " 00:00:00"
            support_num = koubei.xpath(".//label[@class='supportNumber']/text()").extract_first()
            browse_num = koubei.xpath(".//a[@class='orange']/text()").extract_first()
            comment_num = koubei.xpath(".//div[@class='help']/a/span/text()").extract_first()
            url = "https:" + koubei.xpath('.//a[contains(text(),"查看全部内容")]/@href').extract_first()

            meta = {
                "support_num": support_num,
                "posted_time": posted_time,
                "browse_num": browse_num,
                "comment_num": comment_num,
                "bad_msg": bad_msg,
                "brand": response.meta["brand"],
                "factory": response.meta["factory"],
                "series": response.meta["series"],
                "serier_id": response.meta["serier_id"]
            }        
            yield scrapy.Request(url=url, meta=meta, headers=self.headers, 
                                callback=self.parse_koubeidetail)

    def deal_ttf(self, url):
        logging.log(msg=("*" * 50, "deal font   "), level=logging.INFO)
        # font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "koubei.ttf")   
        font_path = '/home/home/baogang/baogang/baogang/koubei.ttf'

        User_Agent = {'User-Agent': get_ug()}
        try:
            text = requests.get(url=url, headers=User_Agent)
        except:
            logging.log(msg='Proxy request timeout Wait for two seconds', level=logging.INFO)
            return 0
        else:
            with open(font_path, "wb") as f:
                f.write(text.content)

        return get_map(font_path)

    def parse_koubeidetail(self, response):
        print("ttf" in response.text)
        try:
            ttf_text_url = "https:" + re.findall(r" url\('(.*)'\) format\('woff'\)", response.text)[0]
        except:
            yield scrapy.Request(url=response.url, meta=response.meta, headers=self.headers,
                                callback=self.parse_koubeidetail)
            return

        font_dict = self.deal_ttf(ttf_text_url)  # 字体映射关系表
        self.driver.get(response.url)
        time.sleep(1)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        content = soup.select('div.text-con')[0].text.strip().replace('\n', '')
        # content
        #  '【最满意】这辆车买\ued6f到现在已经\ued55\uec7d\ueccd几个月\ued5c时间，
        # 使用\ued9c\ued6f对\uec63燃\uec40车，最\ued03感受就\uecfa，\ued6d\uecbb在再去\ued89\uec40站\uec7d，
        for font in font_dict.keys():
            old = r'\u' + font[3:].lower()
            content = re.sub(old, font_dict[font], content)
            content = re.sub(r'\xa0', ' ', content)
            content = re.sub(r'&nbsp;', ' ', content)

        item = Autohome_koubei_all()
        item["grab_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item["posted_time"] = response.meta["posted_time"]
        item["support_num"] = response.meta["support_num"]
        item["browse_num"] = response.meta["browse_num"]
        item["comment_num"] = response.meta["comment_num"]
        item["brand"] = response.meta["brand"]
        item["factory"] = response.meta["factory"]
        item["series"] = response.meta["series"]
        item["car_model"] = response.xpath("//dl[@class='choose-dl']//dd/a[2]/text()").extract_first()
        item["user"] = response.xpath("//a[@id='ahref_UserId']/text()").extract_first()
        item["title"] = response.xpath("//div[@class='kou-tit']//h3/text()").extract_first()
        item["bad_msg"] =str(dict(
            zip(response.xpath("//p[contains(text(),'常规续航里程')]/../p/text()").extract(),
                response.xpath("//p[contains(text(),'常规续航里程')]/../../dd/p/text()").extract())))
        item["content"] = content
        item['url'] = response.url
        item['city'] = response.xpath('//div[@class="choose-con"]//dt[contains(., "购买地点")]').xpath('following-sibling::dd/text()').get().strip()
        item["statusplus"] = item['title'] + item["bad_msg"] + item['series']
        print(item)
        # yield item
