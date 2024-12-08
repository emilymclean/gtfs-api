from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import strptime
from typing import List, Optional, Any, Dict

from .consts import timetable_service_exception_type_pb, service_bikes_allowed, \
    service_wheelchair_accessible, service_bikes_allowed_pb, service_wheelchair_accessible_pb
from .route_timetable_generator import TripInformation, TripStops
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV
from .. import format_pb2 as pb
from ..time_helper import TimeHelper


@dataclass
class RouteTripInformation(Intermediary):
    route_id: str
    service_id: str
    trip_id: str
    trip: TripInformation

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "route_id": self.route_id,
            "trip_id": self.trip_id,
            "trip": self.trip.to_json(time_helper),
        }

    def to_pb(self, info: pb.RouteTripTimetableEndpoint, time_helper: TimeHelper):
        info.serviceId = self.service_id
        info.routeId = self.route_id
        info.tripId = self.trip_id
        self.trip.to_pb(info.trip, time_helper)


class JsonRouteTimetableGeneratorFormat(JsonGeneratorFormat[RouteTripInformation]):

    def parse(self, intermediary: RouteTripInformation, distinguisher: Optional[str]) -> Any:
        return intermediary.to_json(self.time_helper)


class ProtoRouteTimetableGeneratorFormat(ProtoGeneratorFormat[RouteTripInformation]):

    def parse(self, intermediary: RouteTripInformation, distinguisher: Optional[str]) -> Any:
        out = pb.RouteTripTimetableEndpoint()
        intermediary.to_pb(out, self.time_helper)
        return out


class TripTimetableGeneratorComponent(FormatGeneratorComponent[RouteTripInformation]):

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

    def _formats(self) -> List[GeneratorFormat[RouteTripInformation]]:
        return [
            JsonRouteTimetableGeneratorFormat(),
            ProtoRouteTimetableGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteTripInformation, extension: str) -> Path:
        return output_folder.joinpath(
            f"route/{intermediary.route_id}/service/{intermediary.service_id}/trip/{intermediary.trip_id}/timetable.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteTripInformation]:
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.route_data, distinguisher))
        return self._create_intermediary(routes)

    def _create_intermediary(self, routes: List[RouteCSV]) -> List[RouteTripInformation]:
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
                    out.append(
                        RouteTripInformation(
                            r.id,
                            service_id,
                            t.id,
                            TripInformation(
                                stops_for_trip[0].arrival_time if len(stops_for_trip) > 0 else None,
                                stops_for_trip[-1].arrival_time if len(stops_for_trip) > 0 else None,
                                t.wheelchair_accessible,
                                t.bikes_allowed,
                                stops_for_trip
                            )
                        )
                    )

        return out
