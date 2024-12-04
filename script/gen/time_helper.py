from datetime import datetime, timedelta
from time import mktime, strptime
from typing import Any

import pytz


gt_date_format = "%Y%m%d"
gt_time_format = "%H:%M:%S"


class TimeHelper:

    def __init__(self, timezone: str):
        self.region = timezone
        self.timezone = pytz.timezone(timezone)

    def parse_time(self, time: str) -> Any:
        return f"T{time}Z[{self.region}]"

    def parse_date(self, date: str) -> datetime:
        return self._parse(date, gt_date_format)

    def output_time_iso(self, time: Any) -> str:
        return time

    def output_date_iso(self, date: datetime) -> str:
        return date.astimezone(tz=pytz.utc).isoformat()

    def _parse(self, time: str, format: str) -> datetime:
        return datetime.fromtimestamp(mktime(strptime(time, format))).replace(tzinfo=self.timezone)
