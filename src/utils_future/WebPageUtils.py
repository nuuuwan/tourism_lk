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
    def browser_open(url):
        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Firefox(options=options)
        browser.get(url)
        browser.implicitly_wait(2)
        log.debug(f'Opened {url}')
        return browser

    @staticmethod
    def browser_quit(browser):
        browser.quit()
        log.debug('Closed browser')

    @staticmethod
    def scrape_link_urls(url) -> list[str]:
        browser = WebPageUtils.browser_open(url)

        link_urls = []
        for a in browser.find_elements(By.TAG_NAME, 'a'):
            href = a.get_attribute('href')
            link_urls.append(href)

        WebPageUtils.browser_quit(browser)
        link_urls = List(link_urls).unique()

        log.debug(f'Found {len(link_urls)} links on {url}')
        return link_urls

    @staticmethod
    def scrape_pdf_urls(url: str) -> list[str]:
        links = WebPageUtils.scrape_link_urls(url)
        pdf_urls = List(links).filter(lambda link: link.endswith('.pdf'))
        pdf_urls = List(pdf_urls).unique()
        log.debug(f'Found {len(pdf_urls)} PDFs on {url}')
        return pdf_urls
    
    @staticmethod
    def clean_urls(urls: list[str], root_domain: str) -> list[str]:
        cleaned_urls = []
        for page_url_from_child in urls:
            if root_domain not in page_url_from_child:
                continue
            if page_url_from_child.endswith('#'):
                page_url_from_child = page_url_from_child[:-1]
            cleaned_urls.append(page_url_from_child)
        return cleaned_urls

    @staticmethod
    def scrape_pdf_links_recursive(url_root: str, limit: int) -> list[str]:
        log.info(f'Recursively Scraping PDFs from {url_root} (limit={limit})')
        root_domain = url_root.split('/')[2]
        log.debug(f'{root_domain=}')
        page_url_queue = queue.Queue()
        page_url_queue.put(url_root)

        pdf_url_set = set()
        visited_urls = set()
        while True:
            if page_url_queue.empty():
                break
            page_url = page_url_queue.get()
            if page_url in visited_urls:
                continue

            log.debug(f'Visiting {page_url}')
            visited_urls.add(page_url)
            pdf_urls_from_child = WebPageUtils.scrape_pdf_urls(page_url)
            page_urls_from_child = WebPageUtils.scrape_link_urls(page_url)

            cleaned_page_urls_from_child = WebPageUtils.clean_urls(
                page_urls_from_child, root_domain
            )

            log.debug(
                f'Found {len(pdf_urls_from_child)} PDFs,'
                + f' and {len(cleaned_page_urls_from_child)}'+f' links on {page_url}'
                + f' ({len(pdf_url_set)} PDFs found, '
                + f'and {len(visited_urls)} pages visited in total)'
            )

            pdf_url_set.update(pdf_urls_from_child)
            if len(pdf_url_set) >= limit:
                break
            for page_url_from_child in cleaned_page_urls_from_child:
                page_url_queue.put(page_url_from_child)

        log.info(
            f'Found {len(pdf_url_set)} PDFs in total'
            + f' from {url_root} ({len(visited_urls)} pages visited)'
        )
        return list(pdf_url_set)[:limit]

    @staticmethod
    def url_to_file_path_items(url: str) -> str:
        return url.split('/')[3:]

    @staticmethod
    def scrape_and_download(url_root: str, limit: int, dir_root: str):
        log.info(
            f'Scraping and Downloading PDFs from {url_root} (limit={limit})'
        )
        pdf_urls = WebPageUtils.scrape_pdf_links_recursive(url_root, limit)
        for pdf_url in pdf_urls:
            file_path_items = [
                dir_root
            ] + WebPageUtils.url_to_file_path_items(pdf_url)

            dir_path = os.path.join(*file_path_items[:-1])
            # exists_ok: Optional. Default value of this parameter is False. If
            # the specified directory already exists and value is set to False
            # an OSError is raised, else not.
            os.makedirs(dir_path, exist_ok=True)

            file_path = os.path.join(*file_path_items)
            WWW.download_binary(pdf_url, file_path)
            log.debug(f'Downloaded {pdf_url} to {file_path}')
