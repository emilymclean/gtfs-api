from datetime import datetime, timedelta
from time import mktime, strptime
from typing import Any, List

import pytz


gt_date_format = "%Y%m%d"
gt_time_format = "%H:%M:%S"


class TimeHelper:

    def __init__(self, timezone: str):
        self.region = timezone
        self.timezone = pytz.timezone(timezone)

    def parse_time(self, time: str) -> Any:
        parsed = [0, 0, 0]
        components = time.split(":")
        for i in range(0, min(len(components), 3)):
            parsed[i] = int(components[i])
        return parsed

    def parse_date(self, date: str) -> datetime:
        return self._parse(date, gt_date_format)

    def output_time_iso(self, time: Any) -> str:
        time: List[int] = time
        if time[0] > 23:
            return f"P1DT{time[0]-24}H{time[1]}M{time[2]}S"
        return f"PT{time[0]}H{time[1]}M{time[2]}S"

    def output_time_seconds(self, time: Any) -> int:
        time: List[int] = time
        return (time[2]) + (time[1] * 60) + (time[0] * 60 * 60)

    def output_date_iso(self, date: datetime) -> str:
        return date.isoformat()

    def _parse(self, time: str, format: str) -> datetime:
        return datetime.fromtimestamp(mktime(strptime(time, format)))
