import os
import queue
import shutil

from selenium.webdriver.common.by import By
from utils import WWW, Log, String

from utils_future.utils_base.List import List
from utils_future.utils_www.Link import Link
from utils_future.utils_www.WebBrowser import WebBrowser

log = Log('WebScraper')


class WebScraper(WebBrowser):
    @staticmethod
    def scrape_link_list(browser, url) -> list[str]:
        browser = WebScraper.browser_open(browser, url)
        if not browser:
            return []

        link_list = Link.unique(
            List(browser.find_elements(By.TAG_NAME, 'a')).map(
                lambda element_a: Link(element_a)
            )
        )

        log.debug(f'scrape_link_list({url})' + f' -> {len(link_list)} links')
        return link_list

    @classmethod
    def visit_url(cls, browser, url: str, root_domain: str):
        link_list = WebScraper.scrape_link_list(browser, url)
        pdf_link_list = Link.filter_by_ext(link_list, 'pdf')

        page_urls = List(link_list).map(lambda x: x.href)
        cleaned_page_urls = List(page_urls).filter(
            lambda url: (root_domain in url) and cls.is_url_valid(url)
        )

        log.debug(
            f'visit_url({url}) -> {len(pdf_link_list)} pdfs, '
            + f'{len(cleaned_page_urls)} links'
        )

        return pdf_link_list, cleaned_page_urls

    @classmethod
    def scrape_pdf_links_recursive(
        cls, browser, url_root: str, limit: int
    ) -> dict[str, str]:
        log.info(f'Recursively Scraping PDFs from {url_root} (limit={limit})')
        root_domain = url_root.split('/')[2]
        page_url_queue = queue.Queue()
        page_url_queue.put(url_root)

        pdf_link_list = []
        visited_url_set = set()
        while page_url_queue.not_empty and len(pdf_link_list) < limit:
            current_page_url = page_url_queue.get()
            if current_page_url in visited_url_set:
                continue
            (
                pdf_link_list_c,
                cleaned_page_urls_c,
            ) = cls.visit_url(browser, current_page_url, root_domain)
            visited_url_set.add(current_page_url)
            pdf_link_list.extend(pdf_link_list_c)
            for page_url_c in cleaned_page_urls_c:
                page_url_queue.put(page_url_c)
            log.debug(
                f'len(pdf_link_list)={len(pdf_link_list)}, '
                + f'page_url_queue.qsize()={page_url_queue.qsize()}'
            )

        pdf_link_list = Link.unique(pdf_link_list)
        log.info(
            f'Found {len(pdf_link_list)} PDFs in total'
            + f' from {url_root} ({len(visited_url_set)} pages visited)'
        )
        return pdf_link_list

    @classmethod
    def download(cls, pdf_link, dir_root):
        pdf_url = pdf_link.href
        page_url_path_items = cls.url_to_file_path_items(pdf_url)

        dir_path = os.path.join(dir_root, *page_url_path_items)
        os.makedirs(dir_path, exist_ok=True)
        file_name = String(pdf_link.text).kebab + '.pdf'

        file_path = os.path.join(dir_path, file_name)
        if os.path.exists(file_path):
            log.warn(f'Already downloaded {pdf_url} to {file_path}')
        else:
            try:
                WWW.download_binary(pdf_url, file_path)
            except Exception as e:
                log.error(f'WWW.download_binary({pdf_url}) -> {e}')
                return
            log.debug(f'Downloaded {pdf_url} to {file_path}')

    @classmethod
    def scrape_and_download(
        cls, url_root: str, limit: int, dir_root: str, force_clean: bool
    ):
        if force_clean:
            if os.path.exists(dir_root):
                shutil.rmtree(dir_root)
            os.makedirs(dir_root)

        browser = WebScraper.browser_start()

        pdf_link_list = cls.scrape_pdf_links_recursive(
            browser, url_root, limit
        )
        List(pdf_link_list).map_parallel(
            lambda pdf_link: cls.download(pdf_link, dir_root),
            max_threads=5,
        )
        WebScraper.browser_quit(browser)

    # IMPORTANT! classmethods that must be implemented by subclasses

    @classmethod
    def is_url_valid(cls, url):
        raise NotImplementedError

    @classmethod
    def url_to_file_path_items(cls, url: str) -> str:
        raise NotImplementedError
