import os
import shutil

from utils import Log

from tlk.scrapers.CustomWebScraper import CustomWebScraper
from utils_future import SystemMode

log = Log('StatisticsPage')

URL_ROOT = 'https://www.sltda.gov.lk/statistics'
SYSTEM_MODE_ID = SystemMode.get().id

LIMIT = dict(test=5, prod=50).get(SYSTEM_MODE_ID)

DIR_ROOT = os.path.join('data', 'sltda', 'pdf')
FORCE_CLEAN = True


class StatisticsPage:
    def scrape(self):
        if FORCE_CLEAN:
            if os.path.exists(DIR_ROOT):
                shutil.rmtree(DIR_ROOT)
            os.makedirs(DIR_ROOT)
        CustomWebScraper.scrape_and_download(URL_ROOT, LIMIT, DIR_ROOT)
