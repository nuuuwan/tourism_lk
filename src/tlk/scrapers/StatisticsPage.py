import os

from utils import Log

from tlk.scrapers import CustomWebScraper

log = Log('StatisticsPage')

URL_ROOT = 'https://www.sltda.gov.lk/statistics'
LIMIT = 100
DIR_ROOT = os.path.join('data', 'sltda', 'pdf')


class StatisticsPage:
    def scrape(self):
        CustomWebScraper.scrape_and_download(URL_ROOT, LIMIT, DIR_ROOT, True)
