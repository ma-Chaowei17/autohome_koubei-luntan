import os
import sys

from scrapy.cmdline import execute

website = "kangkang_autohome_luntan"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", website])