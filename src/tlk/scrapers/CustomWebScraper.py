from utils_future import List, WebScraper

URL_BLACK_LIST = [
    'careers',
    'download',
    'about-us',
    'contact',
    '.pdf',
    'page=',
]
URL_WHITE_LIST = ['report', 'research']
DIR_NAME_BLACKLIST = ['en', 'statistics']
DOMAIN = 'www.sltda.gov.lk'


class CustomWebScraper(WebScraper):
    @classmethod
    def is_url_valid(cls, url):
        if DOMAIN not in url:
            return False

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
