from abc import ABC
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

import pandas as pd

from .consts import *


class Intermediary(ABC):
    pass


@dataclass
class LocationCSV(Intermediary):
    lat: float
    lng: float

    def to_json(self) -> Dict[str, Any]:
        return {
            "lat": self.lat,
            "lng": self.lng
        }


@dataclass
class StopAccessibilityCSV(Intermediary):
    wheelchair: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "wheelchair": wheelchair_boarding_options[self.wheelchair]
        }


@dataclass
class StopCSV(Intermediary):
    id: str
    name: str
    location: LocationCSV
    accessibility: StopAccessibilityCSV

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location.to_json(),
            "accessibility": self.accessibility.to_json()
        }

    @staticmethod
    def from_csv_row(row: pd.Series) -> "StopCSV":
        return StopCSV(
            f"{row['stop_id']}",
            row['stop_name'],
            LocationCSV(
                row['stop_lat'],
                row['stop_lon'],
            ),
            StopAccessibilityCSV(
                row['wheelchair_boarding']
            )
        )

    @staticmethod
    def from_csv(df: pd.DataFrame) -> List["StopCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(StopCSV.from_csv_row(r))
        return out


@dataclass
class RouteCSV(Intermediary):
    id: str
    code: str
    name: str
    type: int

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "type": route_type_options[self.type],
        }

    @staticmethod
    def from_csv_row(row: pd.Series) -> "RouteCSV":
        return RouteCSV(
            f"{row['route_id']}",
            f"{row['route_short_name']}",
            row['route_long_name'],
            row['route_type'],
        )

    @staticmethod
    def from_csv(df: pd.DataFrame) -> List["RouteCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(RouteCSV.from_csv_row(r))
        return out


@dataclass
class StopTimeCSV(Intermediary):
    trip_id: str
    arrival_time: str
    departure_time: str
    stop_id: str
    stop_sequence: int
    pickup_type: int
    drop_off_type: int
    timepoint: Optional[int]

    @staticmethod
    def from_csv_row(row: pd.Series) -> "StopTimeCSV":
        return StopTimeCSV(
            f"{row['trip_id']}",
            row['arrival_time'],
            row['departure_time'],
            f"{row['stop_id']}",
            row['stop_sequence'],
            row['pickup_type'],
            row['drop_off_type'],
            row['timepoint'] if 'timepoint' in row else None,
        )

    @staticmethod
    def from_csv(df: pd.DataFrame) -> List["StopTimeCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(StopTimeCSV.from_csv_row(r))
        return out


@dataclass
class TripCSV(Intermediary):
    id: str
    route_id: str
    service_id: str
    trip_headsign: str
    direction_id: int

    @staticmethod
    def from_csv_row(row: pd.Series) -> "TripCSV":
        return TripCSV(
            f"{row['trip_id']}",
            f"{row['route_id']}",
            f"{row['service_id']}",
            f"{row['trip_headsign']}",
            row['direction_id'],
        )

    @staticmethod
    def from_csv(df: pd.DataFrame) -> List["TripCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(TripCSV.from_csv_row(r))
        return out


@dataclass
class CalendarCSV(Intermediary):
    service_id: str
    days_of_week: List[bool]
    start_date: str
    end_date: str

    def to_json(self) -> Dict[str, Any]:
        return {
            'monday': self.days_of_week[0],
            'tuesday': self.days_of_week[1],
            'wednesday': self.days_of_week[2],
            'thursday': self.days_of_week[3],
            'friday': self.days_of_week[4],
            'saturday': self.days_of_week[5],
            'sunday': self.days_of_week[6],
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

    @staticmethod
    def from_csv_row(row: pd.Series) -> "CalendarCSV":
        return CalendarCSV(
            f"{row['service_id']}",
            [
                row["monday"] == 1,
                row["tuesday"] == 1,
                row["wednesday"] == 1,
                row["thursday"] == 1,
                row["friday"] == 1,
                row["saturday"] == 1,
                row["sunday"] == 1,
            ],
            f"{row['start_date']}",
            f"{row['end_date']}",
        )

    @staticmethod
    def from_csv(df: pd.DataFrame) -> List["CalendarCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(CalendarCSV.from_csv_row(r))
        return out


@dataclass
class CalendarExceptionCSV(Intermediary):
    service_id: str
    date: str
    type: int

    def to_json(self) -> Dict[str, Any]:
        return {
            'service_id': self.service_id,
            'date': self.date,
            'type': timetable_service_exception_type[self.type],
        }

    @staticmethod
    def from_csv_row(row: pd.Series) -> "CalendarExceptionCSV":
        return CalendarExceptionCSV(
            f"{row['service_id']}",
            f"{row['date']}",
            row['exception_type'],
        )

    @staticmethod
    def from_csv(df: pd.DataFrame) -> List["CalendarExceptionCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(CalendarExceptionCSV.from_csv_row(r))
        return out