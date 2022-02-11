from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By


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

    def get_players(self):
        """
        """

        url = 'https://fantasy.premierleague.com/statistics'
        self._make_driver()
        self._driver.get(url)

        players = []

        while True:
            elements = self._driver.find_elements(By.CSS_SELECTOR, 'tr.ElementTable__ElementRow-sc-1v08od9-3.kGMjuJ')
            for element in elements:
                html = element.get_attribute('innerHTML')
                soup = BeautifulSoup(html, 'lxml')

                name = soup.select('div.ElementInTable__Name-y9xi40-1.dwvEEF')[0].text
                club = soup.select('span.ElementInTable__Team-y9xi40-2.jlsswD')[0].text
                points = int(soup.findAll('td')[5].text)
                form = float(soup.findAll('td')[4].text)
                cost = float(soup.findAll('td')[2].text)
                position = soup.findAll('span')[2].text
                warning = None

                p = f"{name}, {club}, {points}, {form}, {cost}, {position}, {warning}"
                players.append(p)

            try:
                element = self._driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/div[3]/button[3]')
                element.click()
            except (ElementClickInterceptedException, NoSuchElementException):
                # Last page has been reached
                break

        return players


if __name__ == '__main__':
    s = Scraper()
    players = s.get_players()
    for player in players:
        print(player)
