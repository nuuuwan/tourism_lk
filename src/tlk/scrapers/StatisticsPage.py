import os

from utils import Log

from tlk.scrapers.CustomWebScraper import CustomWebScraper
from utils_future import SystemMode

log = Log('StatisticsPage')

URL_ROOT = 'https://www.sltda.gov.lk/statistics'
LIMIT = 1 if SystemMode.is_test() else 100
DIR_ROOT = os.path.join('data', 'sltda', 'pdf')
FORCE_CLEAN = False


class StatisticsPage:
    def scrape(self):
        CustomWebScraper.scrape_and_download(
            URL_ROOT, LIMIT, DIR_ROOT, FORCE_CLEAN
        )
