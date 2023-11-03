from functools import cached_property

from utils_future.utils_base.List import List
from utils_future.utils_www.WebBrowser import WebBrowser


class Link:
    def __init__(self, element_a):
        self.element_a = element_a

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
