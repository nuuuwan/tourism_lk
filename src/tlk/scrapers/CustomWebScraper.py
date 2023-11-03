from utils_future import List, WebScraper

URL_BLACK_LIST = [
    'careers',
    'download',
    'about-us',
    'contact',
    '.pdf',
    'page=',
]
URL_WHITE_LIST = ['report']
DIR_NAME_BLACKLIST = ['en', 'statistics']


class CustomWebScraper(WebScraper):
    @classmethod
    def is_url_valid(cls, url):
        url_lower = url.lower()

        for keyword in URL_BLACK_LIST:
            if keyword in url_lower:
                return False

        for keyword in URL_WHITE_LIST:
            if keyword in url_lower:
                return True
        return False

    @classmethod
    def url_to_file_path_items(cls, url: str) -> str:
        return List(url.split('/')[3:]).filter(
            lambda x: x not in DIR_NAME_BLACKLIST
        )
