import os
import queue

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from utils import WWW, Log

from utils_future import List

log = Log('StatisticsPageUtils')


class WebPageUtils:
    @staticmethod
    def browser_start():
        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Firefox(options=options)
        browser.implicitly_wait(2)
        log.info('🟢browser_start()')
        return browser

    @staticmethod
    def browser_open(browser, url):
        browser.get(url)
        browser.implicitly_wait(2)
        log.info(f'🔵browser_open({url})')
        return browser

    @staticmethod
    def browser_quit(browser):
        browser.quit()
        log.info('🔴browser_quit()')

    @staticmethod
    def scrape_link_urls(browser, url) -> list[str]:
        try:
            browser = WebPageUtils.browser_open(browser, url)
        except Exception as e:
            log.error(f'browser_open({url}) -> {e}')
            return []
        
        link_urls = []
        for a in browser.find_elements(By.TAG_NAME, 'a'):
            href = a.get_attribute('href')
            link_urls.append(href)

        link_urls = List(link_urls).unique()

        log.debug(f'scrape_link_urls({url}) -> {len(link_urls)} links')
        return link_urls

    @staticmethod
    def filter_pdf_urls(urls: list[str]) -> list[str]:
        pdf_urls = List(urls).filter(lambda url: url.endswith('.pdf'))
        pdf_urls = List(pdf_urls).unique()
        log.debug(f'filter_pdf_urls(...) -> {len(pdf_urls)} pdfs')
        return pdf_urls

    @staticmethod
    def is_url_valid(url):
        url_lower = url.lower()
        KEYWORD_BLACK_LIST = ['careers', 'download', 'about-us', 'contact']
        for keyword in KEYWORD_BLACK_LIST:
            if keyword in url_lower:
                return False
        KEYWORD_WHITE_LIST = ['statistics', 'research', 'report']
        for keyword in KEYWORD_WHITE_LIST:
            if keyword in url_lower:
                return True
        return False

    @staticmethod
    def clean_urls(urls: list[str], root_domain: str) -> list[str]:
        cleaned_urls = []
        for page_url_from_child in urls:
            if root_domain not in page_url_from_child:
                continue

            if not WebPageUtils.is_url_valid(page_url_from_child):
                continue

            if page_url_from_child.endswith('#'):
                page_url_from_child = page_url_from_child[:-1]
            cleaned_urls.append(page_url_from_child)
        return cleaned_urls

    @staticmethod
    def visit_url(browser, url: str, root_domain: str):
        log.warn(f'visit_url({url})')
        page_urls = WebPageUtils.scrape_link_urls(browser, url)
        pdf_urls = WebPageUtils.filter_pdf_urls(page_urls)

        cleaned_page_urls = WebPageUtils.clean_urls(page_urls, root_domain)
        log.debug(
            f'visit_url({url}) -> {len(pdf_urls)} pdfs, '
            + f'{len(cleaned_page_urls)} links'
        )

        return pdf_urls, cleaned_page_urls

    @staticmethod
    def scrape_pdf_links_recursive(
        browser, url_root: str, limit: int
    ) -> dict[str, str]:
        log.info(f'Recursively Scraping PDFs from {url_root} (limit={limit})')
        root_domain = url_root.split('/')[2]
        page_url_queue = queue.Queue()
        page_url_queue.put(url_root)

        pdf_info_idx = {}
        visited_url_set = set()
        while page_url_queue.not_empty and len(pdf_info_idx.keys()) < limit:
            current_page_url = page_url_queue.get()
            if current_page_url in visited_url_set:
                continue

            log.debug(f'len(pdf_info_idx)={len(pdf_info_idx.keys())}')
            (
                pdf_urls_from_child,
                cleaned_page_urls_from_child,
            ) = WebPageUtils.visit_url(browser, current_page_url, root_domain)
            visited_url_set.add(current_page_url)

            for pdf_url in pdf_urls_from_child:
                pdf_info_idx[pdf_url] = current_page_url

            for page_url_from_child in cleaned_page_urls_from_child:
                page_url_queue.put(page_url_from_child)

        log.info(
            f'Found {len(pdf_info_idx.keys())} PDFs in total'
            + f' from {url_root} ({len(visited_url_set)} pages visited)'
        )
        return pdf_info_idx

    @staticmethod
    def url_to_file_path_items(url: str) -> str:
        return url.split('/')[3:]

    @staticmethod
    def download(pdf_url, page_url, dir_root):
        pdf_url_path_items = WebPageUtils.url_to_file_path_items(pdf_url)
        page_url_path_items = WebPageUtils.url_to_file_path_items(page_url)

        dir_path = os.path.join(dir_root, *page_url_path_items)
        # exists_ok: Optional. Default value of this parameter is False. If
        # the specified directory already exists and value is set to False
        # an OSError is raised, else not.
        os.makedirs(dir_path, exist_ok=True)

        file_name = pdf_url_path_items[-1]
        file_path = os.path.join(dir_path, file_name)
        if os.path.exists(file_path):
            log.warn(f'Already downloaded {pdf_url} to {file_path}')
        else:
            WWW.download_binary(pdf_url, file_path)
            log.debug(f'Downloaded {pdf_url} to {file_path}')

    @staticmethod
    def scrape_and_download(url_root: str, limit: int, dir_root: str):
        browser = WebPageUtils.browser_start()
        pdf_info_idx = WebPageUtils.scrape_pdf_links_recursive(
            browser, url_root, limit
        )
        List(list(pdf_info_idx.items())).map(
            lambda x: WebPageUtils.download(x[0], x[1], dir_root)
        )
        WebPageUtils.browser_quit(browser)
