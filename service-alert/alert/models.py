from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List


class ServiceAlertRegion(Enum):
    SERVICE_ALERT_REGION_BELCONNEN = 1
    SERVICE_ALERT_REGION_CENTRAL_CANBERRA = 2
    SERVICE_ALERT_REGION_GUNGAHLIN = 3
    SERVICE_ALERT_REGION_TUGGERANONG = 4
    SERVICE_ALERT_REGION_WODEN_WESTON_CREEK_MOLONGLO = 5


@dataclass
class ServiceAlert:
    id: str
    title: str
    date: datetime
    url: str
    regions: List[ServiceAlertRegion]
