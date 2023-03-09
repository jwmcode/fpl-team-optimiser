import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# needed for headless scraping, chrome detects and blocks otherwise
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'


class Scraper:

    def __init__(self, driver='chrome', headless=False):
        self._driver = None
        self._driver_type = driver
        self._headless = headless

    def __del__(self):
        if self._driver:
            self._driver.close()

    def _make_driver(self):
        if self._driver is None:
            if self._driver_type == 'chrome':
                options = webdriver.ChromeOptions()
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--incognito')
                if self._headless:
                    options.add_argument('--headless')
                    options.add_argument(f'user-agent={USER_AGENT}')
                self._driver = webdriver.Chrome(options=options)
                self._driver.implicitly_wait(5)

    def _accept_cookies(self):

        try:
            element = self._driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[5]/button[1]')
            element.click()

        except NoSuchElementException:
            print('no accept cookies element')

    def get_players(self):

        url = 'https://fantasy.premierleague.com/statistics'
        self._make_driver()
        self._driver.get(url)
        self._accept_cookies()

        players_dict = {'second_name': [], 'team': [], 'points': [], 'form': [], 'cost': [], 'position': [],
                        'warning': []}

        while True:
            elements = self._driver.find_elements(By.CSS_SELECTOR, 'tr.ElementTable__ElementRow-sc-1v08od9-3.kGMjuJ')
            for element in elements:
                html = element.get_attribute('innerHTML')
                soup = BeautifulSoup(html, 'lxml')

                players_dict['second_name'].append(soup.select('div.ElementInTable__Name-y9xi40-1.heNyFi')[0].text)
                players_dict['team'].append(soup.select('span.ElementInTable__Team-y9xi40-3.hosEuf')[0].text)
                players_dict['points'].append(int(soup.findAll('td')[5].text))
                players_dict['form'].append(float(soup.findAll('td')[4].text))
                players_dict['cost'].append(float(soup.findAll('td')[2].text))
                players_dict['position'].append(soup.findAll('span')[2].text)
                players_dict['warning'].append(None)

            try:
                WebDriverWait(self._driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div['
                                                                                            '2]/div/div[1]/div['
                                                                                            '3]/button[3]'))).click()

            except (ElementClickInterceptedException, NoSuchElementException, TimeoutException):
                break

        return pd.DataFrame(data=players_dict)


if __name__ == '__main__':
    s = Scraper()
    players = s.get_players()
    print(players)
