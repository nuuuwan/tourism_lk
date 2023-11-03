import os
import queue
import shutil

from selenium.webdriver.common.by import By
from utils import WWW, Log, String

from utils_future import List
from utils_future.WebBrowser import WebBrowser

log = Log('WebScraper')


class WebScraper(WebBrowser):
    @staticmethod
    def scrape_link_url_info_list(browser, url) -> list[str]:
        browser = WebScraper.browser_open(browser, url)
        if not browser:
            return []

        link_url_info_list = []
        for a in browser.find_elements(By.TAG_NAME, 'a'):
            href = a.get_attribute('href')
            text = WebScraper.get_element_text(a)

            url_info = dict(
                href=href,
                text=text,
                url=url,
            )
            link_url_info_list.append(url_info)

        link_url_info_list = List(link_url_info_list).unique_for_key('href')

        log.debug(
            f'scrape_link_url_info_list({url})'
            + f' -> {len(link_url_info_list)} links'
        )
        return link_url_info_list

    @staticmethod
    def filter_pdf_url_info_list(link_url_info_list: list[str]) -> list[str]:
        pdf_url_info_list = List(link_url_info_list).filter(
            lambda url_info: url_info['href'].endswith('.pdf')
        )
        pdf_url_info_list = List(pdf_url_info_list).unique_for_key('href')
        log.debug(
            f'filter_pdf_url_info_list(...) -> {len(pdf_url_info_list)} pdfs'
        )
        return pdf_url_info_list

    @classmethod
    def clean_urls(cls, urls: list[str], root_domain: str) -> list[str]:
        cleaned_urls = []
        for page_url_c in urls:
            if root_domain not in page_url_c:
                continue

            if not cls.is_url_valid(page_url_c):
                continue

            if page_url_c.endswith('#'):
                page_url_c = page_url_c[:-1]
            cleaned_urls.append(page_url_c)
        return cleaned_urls

    @classmethod
    def visit_url(cls, browser, url: str, root_domain: str):
        link_url_info_list = WebScraper.scrape_link_url_info_list(
            browser, url
        )
        pdf_url_info_list = WebScraper.filter_pdf_url_info_list(
            link_url_info_list
        )

        page_urls = List(link_url_info_list).map(lambda x: x['href'])

        cleaned_page_urls = cls.clean_urls(page_urls, root_domain)

        log.debug(
            f'visit_url({url}) -> {len(pdf_url_info_list)} pdfs, '
            + f'{len(cleaned_page_urls)} links'
        )

        return pdf_url_info_list, cleaned_page_urls

    @classmethod
    def scrape_pdf_links_recursive(
        cls, browser, url_root: str, limit: int
    ) -> dict[str, str]:
        log.info(f'Recursively Scraping PDFs from {url_root} (limit={limit})')
        root_domain = url_root.split('/')[2]
        page_url_queue = queue.Queue()
        page_url_queue.put(url_root)

        pdf_url_info_list = []
        visited_url_set = set()
        while page_url_queue.not_empty and len(pdf_url_info_list) < limit:
            current_page_url = page_url_queue.get()
            if current_page_url in visited_url_set:
                continue
            (
                pdf_url_info_list_c,
                cleaned_page_urls_c,
            ) = cls.visit_url(browser, current_page_url, root_domain)
            visited_url_set.add(current_page_url)
            pdf_url_info_list.extend(pdf_url_info_list_c)
            for page_url_c in cleaned_page_urls_c:
                page_url_queue.put(page_url_c)
            log.debug(
                f'len(pdf_url_info_list)={len(pdf_url_info_list)}, '
                + f'page_url_queue.qsize()={page_url_queue.qsize()}'
            )

        pdf_url_info_list = List(pdf_url_info_list).unique_for_key('href')
        log.info(
            f'Found {len(pdf_url_info_list)} PDFs in total'
            + f' from {url_root} ({len(visited_url_set)} pages visited)'
        )
        return pdf_url_info_list

    @classmethod
    def download(cls, pdf_url_info, dir_root):
        pdf_url = pdf_url_info['href']
        page_url_path_items = cls.url_to_file_path_items(pdf_url_info['url'])

        dir_path = os.path.join(dir_root, *page_url_path_items)
        # exists_ok: Optional. Default value of this parameter is False. If
        # the specified directory already exists and value is set to False
        # an OSError is raised, else not.
        os.makedirs(dir_path, exist_ok=True)
        file_name = String(pdf_url_info['text']).kebab + '.pdf'

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

        pdf_url_info_list = cls.scrape_pdf_links_recursive(
            browser, url_root, limit
        )
        List(pdf_url_info_list).map_parallel(
            lambda pdf_url_info: cls.download(pdf_url_info, dir_root),
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
