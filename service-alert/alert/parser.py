import json
from hashlib import sha256
from os import PathLike
from pathlib import Path
from typing import List, Optional

from .models import ServiceAlert, service_alert_region_str, service_alert_region_pb
from .scrapers.base import AlertScraper
from .scrapers.transport_canberra_home_scraper import TransportCanberraHomeScraper
from .scrapers.transport_canberra_alert_scraper import TransportCanberraAlertScraper
from . import format_pb2 as pb


class ServiceAlertParser:

    def __init__(self, scrapers: Optional[List[AlertScraper]] = None):
        self.scrapers = [
            TransportCanberraHomeScraper(),
            TransportCanberraAlertScraper(),
        ] if scrapers is None else scrapers

    def parse(self) -> List[ServiceAlert]:
        alerts = []

        for scraper in self.scrapers:
            alerts += scraper.scrape()

        return alerts

    def output(self, path: str | PathLike):
        alerts = self.parse()

        # Protobuf
        service_alert_endpoint = pb.ServiceAlertEndpoint()
        for alert in alerts:
            pb_alert = pb.ServiceAlert()
            pb_alert.id = alert.id
            pb_alert.title = alert.title
            pb_alert.url = alert.url
            pb_alert.date = alert.date.isoformat()
            for region in alert.regions:
                pb_alert.regions.append(service_alert_region_pb[region.value])

            service_alert_endpoint.alerts.append(pb_alert)

        self._write(
            service_alert_endpoint.SerializeToString(),
            Path(path).joinpath("service-alert.pb")
        )

        # Json
        output = []
        for alert in alerts:
            output.append({
                "id": alert.id,
                "title": alert.title,
                "url": alert.url,
                "date": alert.date.isoformat(),
                "regions": [service_alert_region_str[x.value] for x in alert.regions],
            })

        self._write(
            json.dumps(output),
            Path(path).joinpath("service-alert.json")
        )

    def _write(self, data: bytes | str, path: str | PathLike):
        path = Path(path)
        sha_path = Path(f"{path}.sha")
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            sha = sha256(data).hexdigest()
            with path.open('wb') as f:
                f.write(data)
        else:
            sha = sha256(data.encode('utf-8')).hexdigest()
            with path.open('w') as f:
                f.write(data)

        with sha_path.open('w') as f:
            f.write(sha)
