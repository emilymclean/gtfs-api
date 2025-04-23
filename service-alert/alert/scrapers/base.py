from abc import ABC, abstractmethod
from typing import List

import urllib3
from bs4 import BeautifulSoup

from alert.models import ServiceAlert


class AlertScraper(ABC):

    def _fetch_content(self, url: str) -> BeautifulSoup:
        html = urllib3.request(
            "GET",
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/31.0.1650.16 Safari/537.36"
            }
        ).data

        return BeautifulSoup(html, features="html.parser")

    @abstractmethod
    def scrape(self) -> List[ServiceAlert]:
        pass