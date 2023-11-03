from functools import cached_property

from selenium.webdriver.common.by import By
from utils import Log

from utils_future.utils_base.List import List
from utils_future.utils_www.WebBrowser import WebBrowser

log = Log('Link')


class Link:
    def __init__(self, element_a, page_url):
        self.element_a = element_a
        self.page_url = page_url

    @cached_property
    def href(self):
        return self.element_a.get_attribute('href')

    @cached_property
    def text(self):
        return WebBrowser.get_element_text(self.element_a)

    @staticmethod
    def filter_by_ext(link_list: list['Link'], ext: str) -> list['Link']:
        return List(link_list).filter(
            lambda link: link.href.endswith('.' + ext)
        )

    @staticmethod
    def unique(link_list: list['Link']) -> list['Link']:
        return List(link_list).unique_for_key(lambda x: x.href)

    @staticmethod
    def list_from_url(browser, url) -> list['Link']:
        browser = WebBrowser.browser_open(browser, url)
        if not browser:
            return []

        link_list = Link.unique(
            List(browser.find_elements(By.TAG_NAME, 'a')).map(
                lambda element_a: Link(element_a, url)
            )
        )

        log.debug(
            f'list_from_url(..., {url})' + f' -> {len(link_list)} links'
        )
        return link_list
