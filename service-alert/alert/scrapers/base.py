from abc import ABC, abstractmethod
from typing import List

import cloudscraper
from bs4 import BeautifulSoup

from alert.models import ServiceAlert


class AlertScraper(ABC):

    def _fetch_content(self, url: str) -> BeautifulSoup:
        scraper = cloudscraper.create_scraper()
        html = scraper.get(url).text

        return BeautifulSoup(html, features="html.parser")

    @abstractmethod
    def scrape(self) -> List[ServiceAlert]:
        pass