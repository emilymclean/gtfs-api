from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import strptime
from typing import List, Optional, Any, Dict

from .consts import gt_date_format, timetable_service_exception_type_pb, parse_datetime, service_bikes_allowed, \
    service_wheelchair_accessible
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV
from .. import format_pb2 as pb


@dataclass
class TripStops(Intermediary):
    stop_id: str
    arrival_time: str
    departure_time: str
    sequence: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "stop_id": self.stop_id,
            "arrival_time": self.arrival_time,
            "departure_time": self.departure_time,
            "sequence": self.sequence
        }


@dataclass
class TripInformation(Intermediary):
    start_time: Optional[str]
    end_time: Optional[str]
    wheelchair_accessible: int
    bikes_allowed: int
    stops: List[TripStops]

    def to_json(self) -> Dict[str, Any]:
        return {
            "stops": [x.to_json() for x in self.stops],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "accessibility": {
                "bikesAllowed": service_bikes_allowed[self.bikes_allowed],
                "wheelchairAccessible": service_wheelchair_accessible[self.wheelchair_accessible],
            }
        }


@dataclass
class RouteServiceInformation(Intermediary):
    service_id: str
    trips: List[TripInformation]

    def to_json(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "trips": [x.to_json() for x in self.trips],
        }


@dataclass
class RouteTimetable:
    route_id: str
    information: List[RouteServiceInformation]


class JsonRouteTimetableGeneratorFormat(JsonGeneratorFormat[RouteTimetable]):

    def parse(self, intermediary: RouteTimetable, distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary.information]


class ProtoRouteTimetableGeneratorFormat(ProtoGeneratorFormat[RouteTimetable]):

    def parse(self, intermediary: RouteTimetable, distinguisher: Optional[str]) -> Any:
        out = pb.StopTimetable()

        for t in intermediary.times:
            time = pb.StopTimetableTime()
            time.routeId = t.route_id
            time.routeCode = t.route_code
            time.serviceId = t.service_id
            time.arrivalTime = t.arrival_time
            time.departureTime = t.departure_time
            time.heading = t.heading
            time.sequence = t.sequence

            out.times.append(time)

        return out


class RouteTimetableGeneratorComponent(FormatGeneratorComponent[RouteTimetable]):

    def __init__(
            self,
            route_data: List[ParsedCsv[List[RouteCSV]]],
            trip_index_by_route: Dict[str, List[TripCSV]],
            stop_time_index_by_trip: Dict[str, List[StopTimeCSV]],
            distinguishers: List[str]
    ):
        self.route_data = route_data
        self.trip_index_by_route = trip_index_by_route
        self.stop_time_index_by_trip = stop_time_index_by_trip
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[RouteTimetable]]:
        return [
            JsonRouteTimetableGeneratorFormat(),
            # ProtoRouteTimetableGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteTimetable, extension: str) -> Path:
        return output_folder.joinpath(f"route/{intermediary.route_id}/timetable.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteTimetable]:
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.route_data, distinguisher))
        return self._create_intermediary(routes)

    def _create_intermediary(self, routes: List[RouteCSV]) -> List[RouteTimetable]:
        out = []
        for r in routes:
            trips = self.trip_index_by_route[r.id] if r.id in self.trip_index_by_route else None
            if trips is None:
                out.append(RouteTimetable(
                    r.id, []
                ))
                continue

            service_index = {}
            for t in trips:
                if t.service_id in service_index:
                    service_index[t.service_id].append(t)
                else:
                    service_index[t.service_id] = [t]

            services_for_route = []
            for service_id, service_trips in service_index.items():
                trips_for_service = []
                for t in service_trips:
                    stops_for_trip = [
                        TripStops(
                            s.stop_id,
                            s.arrival_time,
                            s.departure_time,
                            s.stop_sequence
                        )
                        for s in self.stop_time_index_by_trip[t.id]
                    ]
                    trips_for_service.append(
                        TripInformation(
                            stops_for_trip[0].arrival_time if len(stops_for_trip) > 0 else None,
                            stops_for_trip[-1].arrival_time if len(stops_for_trip) > 0 else None,
                            t.wheelchair_accessible,
                            t.bikes_allowed,
                            stops_for_trip
                        )
                    )
                services_for_route.append(
                    RouteServiceInformation(
                        service_id,
                        trips_for_service
                    )
                )
            out.append(RouteTimetable(
                r.id,
                services_for_route
            ))

        return out
