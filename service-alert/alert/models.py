from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from . import format_pb2 as pb


class ServiceAlertRegion(Enum):
    BELCONNEN = 1
    CENTRAL_CANBERRA = 2
    GUNGAHLIN = 3
    TUGGERANONG = 4
    WODEN_WESTON_CREEK_MOLONGLO = 5


service_alert_region_str = ["", "belconnen", "central_canberra", "gungahlin", "tuggeranong",
                            "woden_weston_creek_molonglo"]
service_alert_region_pb = [
    None,
    pb.ServiceAlertRegion.SERVICE_ALERT_REGION_BELCONNEN,
    pb.ServiceAlertRegion.SERVICE_ALERT_REGION_CENTRAL_CANBERRA,
    pb.ServiceAlertRegion.SERVICE_ALERT_REGION_GUNGAHLIN,
    pb.ServiceAlertRegion.SERVICE_ALERT_REGION_TUGGERANONG,
    pb.ServiceAlertRegion.SERVICE_ALERT_REGION_WODEN_WESTON_CREEK_MOLONGLO
]


@dataclass
class ServiceAlert:
    id: str
    title: str
    date: datetime
    url: str
    regions: List[ServiceAlertRegion]
