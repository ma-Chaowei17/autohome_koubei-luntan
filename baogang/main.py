import os
import sys

from scrapy.cmdline import execute

website = "autohome_koubei1"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", website])

