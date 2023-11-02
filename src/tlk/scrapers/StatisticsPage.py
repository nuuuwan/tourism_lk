import os

from utils import Log

from utils_future import WebPageUtils

log = Log('StatisticsPage')

URL_ROOT = 'https://www.sltda.gov.lk/statistics'
LIMIT = 60
DIR_ROOT = os.path.join('data', 'sltda')


class StatisticsPage:
    def scrape(self):
        WebPageUtils.scrape_and_download(URL_ROOT, LIMIT, DIR_ROOT, True)
