import os

from utils import Log

from utils_future import WebPageUtils

log = Log('StatisticsPage')


class StatisticsPage:
    @property
    def url(self) -> str:
        return 'https://www.sltda.gov.lk/statistics'

    @property
    def limit(self) -> int:
        return 100

    @property
    def dir_root(self) -> str:
        return os.path.join('data_source')

    def scrape(self):
        WebPageUtils.scrape_and_download(self.url, self.limit, self.dir_root)
