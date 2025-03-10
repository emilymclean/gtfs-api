from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional

import pandas as pd

from .consts import *
from .extras_helper import _get_route_designation, _get_route_prefix, _get_route_colors, _get_route_real_time, \
    _get_show_on_zoom_out_stop, _get_show_on_zoom_in_stop, _get_show_children_stop, _get_search_weight_stop, \
    _get_search_weight_route, _get_hidden_route
from ..time_helper import TimeHelper


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
    parent_station: Optional[str]
    location: LocationCSV
    accessibility: StopAccessibilityCSV

    @staticmethod
    def from_csv_row(row: pd.Series) -> "StopCSV":
        return StopCSV(
            f"{row['stop_id']}",
            row['stop_name'],
            f"{row['parent_station']}" if 'parent_station' in row and row["parent_station"] != "" else None,
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
class StopIntermediary(Intermediary):
    id: str
    name: str
    parent_station: Optional[str]
    location: LocationCSV
    accessibility: StopAccessibilityCSV
    show_on_zoom_out: bool
    show_on_zoom_in: bool
    show_children: bool
    search_weight: Optional[float]

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "parent_station": self.parent_station,
            "location": self.location.to_json(),
            "accessibility": self.accessibility.to_json(),
            "visibility": {
                "visibleZoomedOut": self.show_on_zoom_out,
                "visibleZoomedIn": self.show_on_zoom_in,
                "showChildren": self.show_children,
                "searchWeight": self.search_weight
            }
        }

    def to_pb(self, stop: pb.Stop):
        stop.id = self.id
        if self.parent_station is not None:
            stop.parentStation = self.parent_station
        stop.name = self.name

        stop.location.lat = self.location.lat
        stop.location.lng = self.location.lng

        stop.accessibility.stopWheelchairAccessible = wheelchair_boarding_options_pb[self.accessibility.wheelchair]

        stop.visibility.visibleZoomedOut = self.show_on_zoom_out
        stop.visibility.visibleZoomedIn = self.show_on_zoom_in
        stop.visibility.showChildren = self.show_children
        if self.search_weight is not None:
            stop.visibility.searchWeight = self.search_weight

    @staticmethod
    def from_csv(
            stop: StopCSV,
            extras: Dict[str, Any]
    ) -> "StopIntermediary":
        show_on_zoom_out = _get_show_on_zoom_out_stop(stop.id, extras)
        show_on_zoom_in = _get_show_on_zoom_in_stop(stop.id, extras)
        show_children = _get_show_children_stop(stop.id, extras)
        search_weight = _get_search_weight_stop(stop.id, extras)

        return StopIntermediary(
            stop.id,
            stop.name,
            stop.parent_station,
            stop.location,
            stop.accessibility,
            show_on_zoom_out,
            show_on_zoom_in,
            show_children,
            search_weight
        )


@dataclass
class RouteCSV(Intermediary):
    id: str
    code: str
    name: str
    type: int


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
class ColorPair(Intermediary):
    color: str
    on_color: str

    def to_json(self) -> dict:
        return {
            "color": self.color,
            "onColor": self.on_color,
        }

    def to_pb(self, route: pb.ColorPair):
        route.color = self.color
        route.onColor = self.on_color


@dataclass
class RouteIntermediary(Intermediary):
    id: str
    code: str
    name: str
    type: int
    designation: Optional[str]
    code_prefix: Optional[str]
    colors: Optional[ColorPair]
    real_time: Optional[str]
    hidden: bool
    search_weight: Optional[float]

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "displayCode": self.code if self.code_prefix is None else f"{self.code_prefix}{self.code}",
            "type": route_type_options[self.type],
            "designation": self.designation,
            "colors": self.colors.to_json() if self.colors is not None else None,
            "realTimeUrl": self.real_time,
            "visibility": {
                "hidden": self.hidden,
                "searchWeight": self.search_weight
            }
        }

    def to_pb(self, route: pb.Route):
        route.id = self.id
        route.code = self.code
        route.displayCode = self.code if self.code_prefix is None else f"{self.code_prefix}{self.code}"
        route.name = self.name
        route.type = route_type_options_pb[self.type]
        if self.designation is not None:
            route.designation = self.designation
        if self.colors is not None:
            self.colors.to_pb(route.colors)
        if self.real_time is not None:
            route.realTimeUrl = self.real_time
        route.routeVisibility.hidden = self.hidden
        if self.search_weight is not None:
            route.routeVisibility.searchWeight = self.search_weight

    @staticmethod
    def from_csv(route: RouteCSV, extras: Dict[str, Any]) -> "RouteIntermediary":
        designation = _get_route_designation(route.code, extras)
        colors = _get_route_colors(route.code, extras)
        search_weight = _get_search_weight_route(route.id, extras)
        hidden = _get_hidden_route(route.id, extras)

        return RouteIntermediary(
            route.id,
            route.code,
            route.name,
            route.type,
            designation,
            _get_route_prefix(designation, extras) if designation is not None else None,
            ColorPair(*colors) if colors is not None else None,
            _get_route_real_time(route.id, extras),
            hidden,
            search_weight
        )


@dataclass
class StopTimeCSV(Intermediary):
    trip_id: str
    arrival_time: Any
    departure_time: Any
    stop_id: str
    stop_sequence: int
    pickup_type: int
    drop_off_type: int
    timepoint: Optional[int]

    @staticmethod
    def from_csv_row(row: pd.Series, time_helper: TimeHelper) -> "StopTimeCSV":
        return StopTimeCSV(
            f"{row['trip_id']}",
            time_helper.parse_time(row['arrival_time']),
            time_helper.parse_time(row['departure_time']),
            f"{row['stop_id']}",
            row['stop_sequence'],
            row['pickup_type'],
            row['drop_off_type'],
            row['timepoint'] if 'timepoint' in row else None,
        )

    @staticmethod
    def from_csv(df: pd.DataFrame, time_helper: TimeHelper) -> List["StopTimeCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(StopTimeCSV.from_csv_row(r, time_helper))
        return out


@dataclass
class TripCSV(Intermediary):
    id: str
    route_id: str
    service_id: str
    trip_headsign: str
    direction_id: int
    wheelchair_accessible: int
    bikes_allowed: int

    @staticmethod
    def from_csv_row(row: pd.Series) -> "TripCSV":
        return TripCSV(
            f"{row['trip_id']}",
            f"{row['route_id']}",
            f"{row['service_id']}",
            f"{row['trip_headsign']}",
            row['direction_id'],
            row['wheelchair_accessible'],
            row['bikes_allowed'],
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
    start_date: datetime
    end_date: datetime

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            'monday': self.days_of_week[0],
            'tuesday': self.days_of_week[1],
            'wednesday': self.days_of_week[2],
            'thursday': self.days_of_week[3],
            'friday': self.days_of_week[4],
            'saturday': self.days_of_week[5],
            'sunday': self.days_of_week[6],
            'start_date': time_helper.output_date_iso(self.start_date),
            'end_date': time_helper.output_date_iso(self.end_date),
        }

    @staticmethod
    def from_csv_row(row: pd.Series, time_helper: TimeHelper) -> "CalendarCSV":
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
            time_helper.parse_date(f"{row['start_date']}"),
            time_helper.parse_date(f"{row['end_date']}"),
        )

    @staticmethod
    def from_csv(df: pd.DataFrame, time_helper: TimeHelper) -> List["CalendarCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(CalendarCSV.from_csv_row(r, time_helper))
        return out


@dataclass
class CalendarExceptionCSV(Intermediary):
    service_id: str
    date: datetime
    type: int

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            'service_id': self.service_id,
            'date': time_helper.output_date_iso(self.date),
            'type': timetable_service_exception_type[self.type],
        }

    @staticmethod
    def from_csv_row(row: pd.Series, time_helper: TimeHelper) -> "CalendarExceptionCSV":
        return CalendarExceptionCSV(
            f"{row['service_id']}",
            time_helper.parse_date(f"{row['date']}"),
            row['exception_type'],
        )

    @staticmethod
    def from_csv(df: pd.DataFrame, time_helper: TimeHelper) -> List["CalendarExceptionCSV"]:
        out = []
        for i, r in df.iterrows():
            out.append(CalendarExceptionCSV.from_csv_row(r, time_helper))
        return out