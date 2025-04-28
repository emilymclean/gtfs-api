from datetime import datetime, timezone
from typing import List
from zoneinfo import ZoneInfo

from alert.models import ServiceAlert, ServiceAlertRegion
from alert.scrapers.base import AlertScraper


class TransportCanberraHomeScraper(AlertScraper):

    def scrape(self) -> List[ServiceAlert]:
        document = self._fetch_content("https://www.transport.act.gov.au/home")
        banner = document.find("div", class_="spf-image-outer banner-outer")
        if banner is None:
            return []

        url = banner.find("a").get("href")
        if url is None:
            return []

        article = self._fetch_content(url)
        title = article.find("meta", attrs={"name": "dcterms.title"}).get("content")
        date = article.find("meta", attrs={"name": "dcterms.date"}).get("content")

        date = (datetime.strptime(date, "%d-%m-%Y")
                .replace(tzinfo=ZoneInfo("Australia/Sydney"))
                .astimezone(timezone.utc))

        return [
            ServiceAlert(
                id=f"{'/'.join(url.split('/')[-2:])}/{date.strftime('%d-%m-%Y')}",
                title=title.strip(),
                url=url,
                date=date,
                regions=[]
            )
        ]
