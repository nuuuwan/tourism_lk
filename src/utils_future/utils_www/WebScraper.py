import os
import queue

from utils import WWW, Log, String

from utils_future.utils_base.List import List
from utils_future.utils_www.Link import Link
from utils_future.utils_www.WebBrowser import WebBrowser

log = Log('WebScraper')


class WebScraper(WebBrowser):
    @classmethod
    def scrape_page_links_recursive(
        cls, browser, url_root: str, limit: int
    ) -> dict[str, str]:
        log.info(
            'Recursively Scraping Pages starting from'
            + f' {url_root} (limit={limit})'
        )
        root_domain = url_root.split('/')[2]
        page_url_queue = queue.Queue()
        page_url_queue.put(url_root)

        visited_url_set = set()
        all_page_urls = []
        while page_url_queue.not_empty and len(all_page_urls) < limit:
            # pre-visit
            current_page_url = page_url_queue.get()
            if current_page_url in visited_url_set:
                continue

            # visit
            child_link_list = Link.list_from_url(browser, current_page_url)
            child_page_urls = List(child_link_list).map(lambda x: x.href)
            child_cleaned_page_urls = List(child_page_urls).filter(
                lambda url: (root_domain in url) and cls.is_url_valid(url)
            )

            # post-visit
            visited_url_set.add(current_page_url)
            for child_page_url in child_cleaned_page_urls:
                page_url_queue.put(child_page_url)

            all_page_urls += child_cleaned_page_urls
            all_page_urls = List(all_page_urls).unique()

            log.debug(f'len(all_page_urls)={len(all_page_urls)}')

        log.info(
            f'Found {len(all_page_urls)} unique URLs' + f' starting from {url_root}.'
        )
        return all_page_urls[:limit]

    @classmethod
    def scrape_pdf_links_recursive(
        cls, browser, url_root: str, limit: int
    ) -> dict[str, str]:
        page_urls = cls.scrape_page_links_recursive(browser, url_root, limit)
        all_pdf_link_list = []
        for page_url in page_urls:
            link_list = Link.list_from_url(browser, page_url)
            pdf_link_list = Link.filter_by_ext(link_list, 'pdf')
            all_pdf_link_list += pdf_link_list
            all_pdf_link_list = Link.unique(all_pdf_link_list)

            log.debug(f'len(all_pdf_link_list)={len(all_pdf_link_list)}')
            if len(all_pdf_link_list) >= limit:
                break
        log.info(
            f'Found {len(all_pdf_link_list)} unique PDFs'
            + f' starting from {url_root}.'
        )

        return all_pdf_link_list[:limit]

    @staticmethod
    def download_if_not_exists(url, file_path):
        if os.path.exists(file_path):
            log.warn(f'Already downloaded {url} to {file_path}')
        else:
            try:
                WWW.download_binary(url, file_path)
            except Exception as e:
                log.error(f'WWW.download_binary({url}) -> {e}')
                return
            log.debug(f'Downloaded {url} to {url}')

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

    # IMPORTANT! classmethods that must be implemented by subclasses

    @classmethod
    def is_url_valid(cls, url):
        raise NotImplementedError

    @classmethod
    def url_to_file_path_items(cls, url: str) -> str:
        raise NotImplementedError
