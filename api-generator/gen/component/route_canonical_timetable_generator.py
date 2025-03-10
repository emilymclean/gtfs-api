from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import strptime
from typing import List, Optional, Any, Dict

from .consts import timetable_service_exception_type_pb, service_bikes_allowed, \
    service_wheelchair_accessible, service_bikes_allowed_pb, service_wheelchair_accessible_pb
from .route_timetable_generator import RouteServiceInformation, JsonRouteTimetableGeneratorFormat, \
    ProtoRouteTimetableGeneratorFormat, TripInformation, TripStops
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV, StopCSV
from .. import format_pb2 as pb
from ..time_helper import TimeHelper


@dataclass
class RouteCanonicalServiceInformation(Intermediary):
    route_id: str
    service_id: str
    trip: TripInformation

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "route_id": self.route_id,
            "trip": self.trip.to_json(time_helper),
        }

    def to_pb(self, info: pb.RouteCanonicalTimetableEndpoint, time_helper: TimeHelper):
        info.serviceId = self.service_id
        info.routeId = self.route_id
        self.trip.to_pb(info.trip, time_helper)


class JsonRouteCanonicalTimetableGeneratorFormat(JsonGeneratorFormat[RouteCanonicalServiceInformation]):

    def parse(self, intermediary: RouteCanonicalServiceInformation, distinguisher: Optional[str]) -> Any:
        return intermediary.to_json(self.time_helper)


class ProtoRouteCanonicalTimetableGeneratorFormat(ProtoGeneratorFormat[RouteCanonicalServiceInformation]):

    def parse(self, intermediary: RouteCanonicalServiceInformation, distinguisher: Optional[str]) -> Any:
        out = pb.RouteCanonicalTimetableEndpoint()
        intermediary.to_pb(out, self.time_helper)
        return out


class RouteCanonicalTimetableGeneratorComponent(FormatGeneratorComponent[RouteCanonicalServiceInformation]):

    def __init__(
            self,
            route_data: List[ParsedCsv[List[RouteCSV]]],
            trip_index_by_route: Dict[str, List[TripCSV]],
            stop_time_index_by_trip: Dict[str, List[StopTimeCSV]],
            stop_index: Dict[str, StopCSV],
            distinguishers: List[str]
    ):
        self.route_data = route_data
        self.trip_index_by_route = trip_index_by_route
        self.stop_time_index_by_trip = stop_time_index_by_trip
        self.stop_index = stop_index
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[RouteCanonicalServiceInformation]]:
        return [
            JsonRouteCanonicalTimetableGeneratorFormat(),
            ProtoRouteCanonicalTimetableGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteCanonicalServiceInformation, extension: str) -> Path:
        return output_folder.joinpath(f"route/{intermediary.route_id}/service/{intermediary.service_id}/canonical.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteCanonicalServiceInformation]:
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.route_data, distinguisher))
        return self._create_intermediary(routes)

    def _parent_stop(self, stop_id: str) -> StopCSV:
        stop = self.stop_index[stop_id]
        if stop.parent_station is None:
            return stop
        else:
            return self._parent_stop(stop.parent_station)

    def _create_intermediary(self, routes: List[RouteCSV]) -> List[RouteCanonicalServiceInformation]:
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
                    stops_for_trip = []
                    for s in self.stop_time_index_by_trip[t.id]:
                        parentStop = self._parent_stop(s.stop_id).id
                        stops_for_trip.append(TripStops(
                            parentStop,
                            None,
                            None,
                            s.stop_sequence,
                            s.stop_id if s.stop_id != parentStop else None,
                        ))
                    trips_for_service.append(
                        TripInformation(
                            None,
                            None,
                            t.wheelchair_accessible,
                            t.bikes_allowed,
                            stops_for_trip
                        )
                    )
                canonical = max(set(trips_for_service), key=trips_for_service.count)
                out.append(
                    RouteCanonicalServiceInformation(
                        r.id,
                        service_id,
                        canonical
                    )
                )

        return out
