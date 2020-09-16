# -*-coding:utf-8-*-
import base64
import logging
import re
import time
import random

import execjs
import requests
from pybloom_live import ScalableBloomFilter
from scrapy.conf import settings
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.http import HtmlResponse
import json
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy.utils.response import response_status_message

fail_url_text_name = "fail_url_text_name"
num = (2000000) * 1.1
dff = ScalableBloomFilter(initial_capacity=num, error_rate=0.001)
user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6',
    'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6',
    'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.3 Mobile/14E277 Safari/603.1.30',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
]


def get_ug():
    ua = random.choice(user_agent_list)
    return ua


class AutohomeProxyMiddleware(object):
    def __int__(self):
        pass

    def get_Proxy(self):
        url = 'http://120.27.216.150:5000'
        headers = {
            'Connection': 'close',
        }

        proxy = requests.get(url, auth=('admin', 'zd123456'), headers=headers, timeout=5).text[0:-6]
        return proxy

    def process_request(self, request, spider):
        # print(request.url,"-"*50)
        proxy = self.get_Proxy()
        # print(request.meta['splash']['args']['proxy'])
        # http://120.27.216.150:5000
        if "192.168.1.172:8050" in request.url:
            request.meta['splash']['args']['proxy'] = "http://" + proxy
            request.meta['splash']['args'][
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
            logging.log(msg="splash" + "*" * 50 + "use           " + proxy + "*" * 50 + request.url, level=logging.INFO)

        # elif "192.168.1.172:8050" in request.url:
        #     return request
        else:
            logging.log(msg="scrapy" + "*" * 50 + "use           " + proxy + "*" * 50 + request.url, level=logging.INFO)

            request.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
            request.meta['proxy'] = "http://" + proxy

    def process_response(self, request, response, spider):
        # print(response.status)
        # print(request.headers)
        if response.status != 200:
            logging.log(msg='this request is  bad {}'.format(request.url), level=logging.INFO)
            proxy = self.get_Proxy()
            request.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
            request.meta['proxy'] = "http://" + proxy
            return request
        else:
            return response


class zhilian():
    def __init__(self):
        self.js = r"""function geta(a){
      var a  =a;
          var _0x4b082b = [0xf, 0x23, 0x1d, 0x18, 0x21, 0x10, 0x1, 0x26, 0xa, 0x9, 0x13, 0x1f, 0x28, 0x1b, 0x16, 0x17, 0x19, 0xd, 0x6, 0xb, 0x27, 0x12, 0x14, 0x8, 0xe, 0x15, 0x20, 0x1a, 0x2, 0x1e, 0x7, 0x4, 0x11, 0x5, 0x3, 0x1c, 0x22, 0x25, 0xc, 0x24];
          var _0x4da0dc = [];
          var _0x12605e = '';
          for (var _0x20a7bf = 0x0; _0x20a7bf < a['\x6c\x65\x6e\x67\x74\x68']; _0x20a7bf++) {
              var _0x385ee3 = a[_0x20a7bf];
              for (var _0x217721 = 0x0; _0x217721 < _0x4b082b["length"]; _0x217721++) {
                  if (_0x4b082b[_0x217721] == _0x20a7bf + 0x1) {
                      _0x4da0dc[_0x217721] = _0x385ee3;
                  }
              }
          }
          _0x12605e = _0x4da0dc['\x6a\x6f\x69\x6e']('');
          return _0x12605e;

      }

      // 6E1483F2D8F3BF8F07D3B3926E0BA02ACCF2C16B
      function getb(c){
      var _0x4e08d8="3000176000856006061501533003690027800375"
         var c =c
              var _0x5a5d3b = '';
              for (var _0xe89588 = 0x0; _0xe89588 < c["length"] && _0xe89588 < _0x4e08d8["length"]; _0xe89588 += 0x2) {
                  var _0x401af1 = parseInt(c["slice"](_0xe89588, _0xe89588 + 0x2), 0x10);
                  var _0x105f59 = parseInt(_0x4e08d8["slice"](_0xe89588, _0xe89588 + 0x2), 0x10);
                  var _0x189e2c = (_0x401af1 ^ _0x105f59)["toString"](0x10);
                  if (_0x189e2c["length"] == 0x1) {
                      _0x189e2c = '\x30' + _0x189e2c;
                  }
                  _0x5a5d3b += _0x189e2c;
              }
              return _0x5a5d3b;
      }
      function getpwd(a){
          var c = geta(a)
          var b =getb(c)
          return b



      }
    """
        self.cookie = ''
        self.header = get_ug()

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.header
        request.cookies = {"acw_sc__v2": self.cookie}

    def process_response(self, request, response, spider):
        print('var arg1=' in response.text)
        if 'var arg1=' in response.text:
            code = re.findall(r"var arg1='(.*?)';", response.text)[0]
            print(code)
            Cookie = execjs.compile(self.js).call('getpwd', code)
            self.cookie = Cookie
            self.header = get_ug()
            request.headers['User-Agent'] = self.header
            request.cookies = {"acw_sc__v2": self.cookie}
            return request
        else:
            return response


class ProxyMiddleware(object):
    def __int__(self):
        pass

    def get_Proxy(self):
        url = 'http://120.27.216.150:5000'
        headers = {
            'Connection': 'close',
        }

        proxy = requests.get(url, auth=('admin', 'zd123456'), headers=headers, timeout=5).text[0:-6]
        return proxy

    def process_request(self, request, spider):
        if spider.name not in ["yiche_paihang", "yiche_dianping"]:
            # User_Agent = {'User-Agent': get_ug()}
            proxy = self.get_Proxy()
            logging.log(msg="use           " + proxy, level=logging.INFO)
            # request.headers = Headers(headers)
            request.headers['User-Agent'] = get_ug()
            request.meta['proxy'] = "http://" + proxy

    def process_response(self, request, response, spider):
        # print(request.headers)
        if response.status == 302:
            return request
        else:
            return response

    #  如果发生链接不生的情况 重新链接
    def proccess_exception(self, request, exception, spider):
        logging.log(msg="-----------------------ceshi----------------", level=logging.INFO)
        if isinstance(exception, TimeoutError):
            logging.log(msg="------------------------TimeoutError-------------------", level=logging.INFO)
            return request
        elif isinstance(exception, TCPTimedOutError):
            logging.log(msg="------------------------TCPTimedOutError-------------------", level=logging.INFO)
            return request


class MyRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        # print("*" * 50)
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            returndf = dff.add(request.url)  # df 为布隆过滤器  存在1 不存在0
            if returndf:  # 如果存在
                pass
            else:  # 数据有效    数据为空  的情况下 处理
                with open(fail_url_text_name, "a", encoding="utf-8")as f:
                    f.writelines(request.url + "\n")
                    logging.log(msg="fail request          " + request.url, level=logging.INFO)
            return self._retry(request, reason, spider) or response
        return response
