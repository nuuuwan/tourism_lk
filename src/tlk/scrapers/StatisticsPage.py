import os

from utils import Log

from utils_future import WebPageUtils

log = Log('StatisticsPage')

URL_ROOT = 'https://www.sltda.gov.lk/statistics'
LIMIT = 100
DIR_ROOT = os.path.join('data_source')


class StatisticsPage:
    def scrape(self):
        WebPageUtils.scrape_and_download(URL_ROOT, DIR_ROOT, LIMIT)
