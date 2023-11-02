import os

from utils import WWW, Log

from utils_future import WebPageUtils

log = Log('StatisticsPage')


class StatisticsPage:
    @property
    def url(self) -> str:
        return 'https://www.sltda.gov.lk/statistics'

    @property
    def limit(self) -> int:
        return 3

    def scrape(self):
        pdf_urls = WebPageUtils.scrape_pdf_links_recursive(
            self.url, self.limit
        )
        for pdf_url in pdf_urls:
            file_path_items = [
                'data_source'
            ] + WebPageUtils.url_to_file_path_items(pdf_url)

            dir_path = os.path.join(*file_path_items[:-1])
            # exists_ok: Optional. Default value of this parameter is False. If
            # the specified directory already exists and value is set to False
            # an OSError is raised, else not.
            os.makedirs(dir_path, exist_ok=True)

            file_path = os.path.join(*file_path_items)
            WWW.download_binary(pdf_url, file_path)
            log.debug(f'Downloaded {pdf_url} to {file_path}')
