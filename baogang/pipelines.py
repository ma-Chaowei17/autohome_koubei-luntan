# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import logging
import pymongo

import pandas as pd

from sqlalchemy import create_engine
from scrapy.conf import settings
from .redis_bloom import BloomFilter


class GuaziPipeline(object):

    def __init__(self):
        # def __init__(self,settings):
        self.count = 0
        self.engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(settings['MYSQLDB_USER'],
                                                                                         settings['MYSQLDB_PASS'],
                                                                                         settings['MYSQL_SERVER'],
                                                                                         settings['MYSQL_PORT'],
                                                                                         settings['MYSQLDB_DB'], ))

        self.connection = pymongo.MongoClient(
            settings["MONGODB_SERVER"],
            settings["MONGODB_PORT"]
        )
        db = self.connection[settings["MONGODB_DB"]]
        self.collection = db[settings["MONGODB_COLLECTION"]]
        # print("82"  ,settings["WEBSITE"])
        self.bf = BloomFilter(key='b1f_' + settings["WEBSITE"])
        # self.bf = BloomFilter(key='b1f_guazi')

        # self.settings = settings)

    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler.settings)

    def process_item(self, item, spider):
        #  用来去重的键 statusplus
        # print(settings['MYSQLDB_DB'], '*******************' * 50)
        item["statusplus"] = hashlib.md5(str(item["statusplus"]).encode("utf-8")).hexdigest()
        returndf = self.bf.isContains(item["statusplus"])
        # print(settings["WEBSITE"] + "_online")

        # 1数据存在，0数据不存在
        if returndf == 1:
            logging.log(msg="Car duplication!!!!", level=logging.INFO)
            return item
        else:
            self.count = self.count + 1
            self.bf.insert(item["statusplus"])
            # 如果不在 列表内，存mysql  如果在 存 mongodb
            if spider.name not in [""]:
                try:
                    df = pd.DataFrame([item])
                    df.to_sql(name=settings["WEBSITE"], con=self.engine, if_exists="append", index=False)
                except Exception as e:
                    logging.log(msg="fail to save  %s" % e, level=logging.INFO)
                else:
                    logging.log(msg="add car in SQL %d" % self.count, level=logging.INFO)
                finally:
                    return item
            else:
                try:
                    self.collection.insert(dict(item))
                except Exception as e:
                    logging.log(msg="fail to save  %s" % e, level=logging.INFO)
                else:
                    logging.log(msg="add car in MONGODB %d" % self.count, level=logging.INFO)
                finally:
                    return item
