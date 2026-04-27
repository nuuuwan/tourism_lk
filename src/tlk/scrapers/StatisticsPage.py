import os
import shutil

from utils import Log

from tlk.scrapers.CustomWebScraper import CustomWebScraper
from utils_future import SystemMode, List

log = Log('StatisticsPage')

URL_ROOTS = [
    'https://www.sltda.gov.lk/statistics',
    'https://www.sltda.gov.lk/en/weekly-tourist-arrivals-reports-2026',
    'https://www.sltda.gov.lk/en/monthly-tourist-arrivals-reports-2026',
]
LIMIT = SystemMode.get_if(test=1, prod=100)

DIR_ROOT = os.path.join('data', 'sltda', 'pdf')
FORCE_CLEAN = False


class StatisticsPage:
    def scrape(self):
        if FORCE_CLEAN:
            if os.path.exists(DIR_ROOT):
                shutil.rmtree(DIR_ROOT)
            os.makedirs(DIR_ROOT)
        
        all_pdf_link_list = []
        for url_root in URL_ROOTS:
            pdf_link_list = CustomWebScraper.scrape_and_download(url_root, LIMIT, DIR_ROOT)
            all_pdf_link_list.extend(pdf_link_list)
        return all_pdf_link_list
