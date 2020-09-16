import os
import sys

from scrapy.cmdline import execute

website = "kang_autohome_koubei"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", website])