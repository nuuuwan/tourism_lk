import os

from utils import WWW, Log, String

from utils_future.utils_base.List import List
from utils_future.utils_base.QueueProcessor import QueueProcessor
from utils_future.utils_www.Link import Link
from utils_future.utils_www.WebBrowser import WebBrowser

log = Log('WebScraper')


class WebScraper(WebBrowser):
    @staticmethod
    def clean_url(url):
        return url.split('#')[0]

    @classmethod
    def scrape_pdf_links_recursive(
        cls, browser, url_root: str, limit: int
    ) -> dict[str, str]:
        url_root.split('/')[2]

        def func_process(url: str):
            link_list = Link.list_from_url(browser, url)
            pdf_link_list = Link.filter_by_ext(link_list, 'pdf')
            new_urls = List(link_list).map(lambda x: x.href)
            cleaned_new_urls = List(
                List(new_urls).map(WebScraper.clean_url)
            ).filter(cls.is_url_valid)
            return cleaned_new_urls, pdf_link_list

        def func_end(url_list: list[str]):
            return len(url_list) > limit

        all_pdf_link_list = QueueProcessor.run(
            [url_root],
            func_process,
            func_end,
        )
        log.info(
            f'Found {len(all_pdf_link_list)} unique PDFs'
            + f' starting from {url_root}.'
        )
        return all_pdf_link_list[:limit]

    @staticmethod
    def download_if_not_exists(url, file_path):
        if os.path.exists(file_path):
            log.warn(f'Already downloaded {url} -> {file_path}')
            return

        try:
            WWW.download_binary(url, file_path)
            log.debug(f'Downloaded {url} -> {file_path}')
        except Exception as e:
            log.error(f'WWW.download_binary({url}) -> {e}')

    @classmethod
    def get_dir_path_for_url(cls, pdf_link: Link, dir_root: str) -> str:
        page_url_path_items = cls.url_to_file_path_items(pdf_link.page_url)
        dir_path = os.path.join(dir_root, *page_url_path_items)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    @classmethod
    def download(cls, pdf_link, dir_root):
        dir_path = cls.get_dir_path_for_url(pdf_link, dir_root)
        file_path = os.path.join(
            dir_path, String(pdf_link.text).kebab + '.pdf'
        )
        pdf_link.local_file_path = file_path
        WebScraper.download_if_not_exists(pdf_link.href, file_path)

    @classmethod
    def scrape_and_download(cls, url_root: str, limit: int, dir_root: str):
        browser = WebScraper.browser_start()
        pdf_link_list = cls.scrape_pdf_links_recursive(
            browser, url_root, limit
        )
        List(pdf_link_list).map_parallel(
            lambda pdf_link: cls.download(pdf_link, dir_root),
            max_threads=4,
        )
        WebScraper.browser_quit(browser)
        return pdf_link_list

    # IMPORTANT! classmethods that must be implemented by subclasses

    @classmethod
    def is_url_valid(cls, url):
        raise NotImplementedError

    @classmethod
    def url_to_file_path_items(cls, url: str) -> str:
        raise NotImplementedError
