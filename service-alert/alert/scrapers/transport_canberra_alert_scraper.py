from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from alert.models import ServiceAlert, ServiceAlertRegion
from alert.scrapers.base import AlertScraper


class TransportCanberraAlertScraper(AlertScraper):

    def fallback_title(self, href: str) -> Optional[str]:
        document = self._fetch_content(href)
        title = document.find("h1", {"id": "page_title"}).text

        if title.isspace() or title == "":
            return None

        return title

    def scrape(self) -> List[ServiceAlert]:
        document = self._fetch_content("https://www.transport.act.gov.au/news/service-alerts-and-updates")
        articles = document.find_all("article")
        alerts = []

        for article in articles:
            title = article.find("h2").text
            url = article.find("a")["href"]
            date = article.find("date").text.replace("Posted: ", "").strip()
            region = article.find("br").next_sibling.text.replace("Region: ", "").strip()

            if title.isspace() or title == "":
                title = self.fallback_title(url)
            if title is None:
                title = "No title provided"

            date = (datetime.strptime(date, "%d %b %Y")
                    .replace(tzinfo=ZoneInfo("Australia/Sydney"))
                    .astimezone(timezone.utc))

            regions = []
            match region:
                case "Belconnen":
                    regions.append(ServiceAlertRegion.BELCONNEN)
                case "Central Canberra":
                    regions.append(ServiceAlertRegion.CENTRAL_CANBERRA)
                case "Gungahlin":
                    regions.append(ServiceAlertRegion.GUNGAHLIN)
                case "Tuggeranong":
                    regions.append(ServiceAlertRegion.TUGGERANONG)
                case "Woden, Weston Creek and Molonglo":
                    regions.append(ServiceAlertRegion.WODEN_WESTON_CREEK_MOLONGLO)

            alerts.append(ServiceAlert(
                id=f"{'/'.join(url.split('/')[-2:])}/{date.strftime('%d-%m-%Y')}",
                title=title.strip(),
                url=url,
                date=date,
                regions=regions
            ))

        return alerts