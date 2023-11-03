import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from utils import Log

log = Log('WebBrowser')


class WebBrowser:
    @staticmethod
    def browser_start():
        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Firefox(options=options)
        browser.implicitly_wait(2)
        log.debug('🟢browser_start()')
        return browser

    @staticmethod
    def browser_open_unsafe(browser, url):
        browser.get(url)
        time.sleep(2)
        log.debug(f'🔵browser_open({url})')
        return browser

    @staticmethod
    def browser_open(browser, url):
        try:
            browser = WebBrowser.browser_open_unsafe(browser, url)
        except Exception as e:
            log.error(f'browser_open({url}) -> {e}')
            return None
        return browser

    @staticmethod
    def browser_quit(browser):
        browser.quit()
        log.debug('🔴browser_quit()')

    @staticmethod
    def get_element_text(element):
        current_element = element
        while True:
            text = current_element.text
            if len(text) > 128:
                return ''
            if text and len(text) > 5:
                return text
            current_element = current_element.find_element(By.XPATH, '..')
            if current_element.tag_name == 'html':
                return ''
