from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import strptime
from typing import List, Optional, Any, Dict

from .consts import timetable_service_exception_type_pb, service_bikes_allowed, \
    service_wheelchair_accessible, service_bikes_allowed_pb, service_wheelchair_accessible_pb
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV
from .. import format_pb2 as pb
from ..time_helper import TimeHelper


@dataclass
class TripStops(Intermediary):
    stop_id: str
    arrival_time: Optional[Any]
    departure_time: Optional[Any]
    sequence: int
    child_stop_id: Optional[str] = None

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "stop_id": self.stop_id,
            "child_stop_id": self.child_stop_id,
            "arrival_time": time_helper.output_time_iso(self.arrival_time) if self.arrival_time is not None else None,
            "departure_time": time_helper.output_time_iso(self.departure_time) if self.departure_time is not None else None,
            "sequence": self.sequence
        }

    def to_pb(self, stop: pb.RouteTripStop, time_helper: TimeHelper):
        stop.stopId = self.stop_id
        if self.child_stop_id is not None:
            stop.childStopId = self.child_stop_id
        if self.arrival_time is not None:
            stop.arrivalTime = time_helper.output_time_iso(self.arrival_time)
        if self.departure_time is not None:
            stop.departureTime = time_helper.output_time_iso(self.departure_time)
        stop.sequence = self.sequence

    def __hash__(self) -> int:
        return hash(f"{self.stop_id}|{self.sequence}|{self.arrival_time}|{self.departure_time}")


@dataclass
class TripInformation(Intermediary):
    start_time: Optional[Any]
    end_time: Optional[Any]
    wheelchair_accessible: int
    bikes_allowed: int
    stops: List[TripStops]

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "stops": [x.to_json(time_helper) for x in self.stops],
            "start_time": time_helper.output_time_iso(self.start_time) if self.start_time is not None else None,
            "end_time": time_helper.output_time_iso(self.end_time) if self.end_time is not None else None,
            "accessibility": {
                "bikesAllowed": service_bikes_allowed[self.bikes_allowed],
                "wheelchairAccessible": service_wheelchair_accessible[self.wheelchair_accessible],
            }
        }

    def to_pb(self, info: pb.RouteTripInformation, time_helper: TimeHelper):
        if self.start_time is not None:
            info.startTime = time_helper.output_time_iso(self.start_time)
        if self.end_time is not None:
            info.endTime = time_helper.output_time_iso(self.end_time)
        info.accessibility.bikesAllowed = service_bikes_allowed_pb[self.bikes_allowed]
        info.accessibility.wheelchairAccessible = service_wheelchair_accessible_pb[self.wheelchair_accessible]

        for stop in self.stops:
            p = pb.RouteTripStop()
            stop.to_pb(p, time_helper)
            info.stops.append(p)

    def __hash__(self) -> int:
        ret = hash(f"{self.start_time}|{self.end_time}|{self.wheelchair_accessible}|{self.bikes_allowed}")
        for stop in self.stops:
            ret += hash(stop)
        return int(ret)


@dataclass
class RouteServiceInformation(Intermediary):
    route_id: str
    service_id: str
    trips: List[TripInformation]

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "route_id": self.route_id,
            "trips": [x.to_json(time_helper) for x in self.trips],
        }

    def to_pb(self, info: pb.RouteTimetableEndpoint, time_helper: TimeHelper):
        info.serviceId = self.service_id
        info.routeId = self.route_id

        for trip in self.trips:
            p = pb.RouteTripInformation()
            trip.to_pb(p, time_helper)
            info.trips.append(p)


class JsonRouteTimetableGeneratorFormat(JsonGeneratorFormat[RouteServiceInformation]):

    def parse(self, intermediary: RouteServiceInformation, distinguisher: Optional[str]) -> Any:
        return intermediary.to_json(self.time_helper)


class ProtoRouteTimetableGeneratorFormat(ProtoGeneratorFormat[RouteServiceInformation]):

    def parse(self, intermediary: RouteServiceInformation, distinguisher: Optional[str]) -> Any:
        out = pb.RouteTimetableEndpoint()
        intermediary.to_pb(out, self.time_helper)
        return out


class RouteTimetableGeneratorComponent(FormatGeneratorComponent[RouteServiceInformation]):

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

    def _formats(self) -> List[GeneratorFormat[RouteServiceInformation]]:
        return [
            JsonRouteTimetableGeneratorFormat(),
            ProtoRouteTimetableGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteServiceInformation, extension: str) -> Path:
        return output_folder.joinpath(
            f"route/{intermediary.route_id}/service/{intermediary.service_id}/timetable.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteServiceInformation]:
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.route_data, distinguisher))
        return self._create_intermediary(routes)

    def _create_intermediary(self, routes: List[RouteCSV]) -> List[RouteServiceInformation]:
        out = []
        for r in routes:
            trips = self.trip_index_by_route[r.id] if r.id in self.trip_index_by_route else None
            if trips is None:
                continue

            service_index = {}
            for t in trips:
                if t.service_id in service_index:
                    service_index[t.service_id].append(t)
                else:
                    service_index[t.service_id] = [t]

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
                out.append(
                    RouteServiceInformation(
                        r.id,
                        service_id,
                        trips_for_service
                    )
                )

        return out
