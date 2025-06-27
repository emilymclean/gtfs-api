from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any, Dict

from ... import format_pb2 as pb
from ..base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from ..intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, StopCSV
from ..route_timetable_generator import TripInformation, TripStops
from ...models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from ...time_helper import TimeHelper


@dataclass
class RouteCanonicalServiceInformationV2(Intermediary):
    route_id: str
    service_id: str
    trips: List[TripInformation]

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "trips": [trip.to_json(time_helper) for trip in self.trips],
        }

    def to_pb(self, info: pb.RouteCanonicalTimetableEndpointV2, time_helper: TimeHelper):
        for trip in self.trips:
            p = pb.RouteTripInformation()
            trip.to_pb(p, time_helper)
            info.trips.append(p)


class JsonRouteCanonicalTimetableGeneratorV2Format(JsonGeneratorFormat[RouteCanonicalServiceInformationV2]):

    def parse(self, intermediary: RouteCanonicalServiceInformationV2, distinguisher: Optional[str]) -> Any:
        return intermediary.to_json(self.time_helper)


class ProtoRouteCanonicalTimetableGeneratorV2Format(ProtoGeneratorFormat[RouteCanonicalServiceInformationV2]):

    def parse(self, intermediary: RouteCanonicalServiceInformationV2, distinguisher: Optional[str]) -> Any:
        out = pb.RouteCanonicalTimetableEndpointV2()
        intermediary.to_pb(out, self.time_helper)
        return out


class RouteCanonicalTimetableGeneratorV2Component(FormatGeneratorComponent[RouteCanonicalServiceInformationV2]):

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

    def _formats(self) -> List[GeneratorFormat[RouteCanonicalServiceInformationV2]]:
        return [
            JsonRouteCanonicalTimetableGeneratorV2Format(),
            ProtoRouteCanonicalTimetableGeneratorV2Format()
        ]

    def _path(self, output_folder: Path, intermediary: RouteCanonicalServiceInformationV2, extension: str) -> Path:
        return output_folder.joinpath(f"v2/route/{intermediary.route_id}/service/{intermediary.service_id}/canonical.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteCanonicalServiceInformationV2]:
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.route_data, distinguisher))
        return self._create_intermediary(routes)

    def _parent_stop(self, stop_id: str) -> StopCSV:
        stop = self.stop_index[stop_id]
        if stop.parent_station is None:
            return stop
        else:
            return self._parent_stop(stop.parent_station)

    def _create_intermediary(self, routes: List[RouteCSV]) -> List[RouteCanonicalServiceInformationV2]:
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
                trips_for_service = {}
                for t in service_trips:
                    stops_for_trip = []
                    for s in self.stop_time_index_by_trip[t.id]:
                        parent_stop = self._parent_stop(s.stop_id).id
                        stops_for_trip.append(TripStops(
                            parent_stop,
                            None,
                            None,
                            s.stop_sequence,
                            s.stop_id if s.stop_id != parent_stop else None,
                        ))

                    if (t.service_id, t.trip_headsign) not in trips_for_service:
                        trips_for_service[(t.service_id, t.trip_headsign)] = []
                    trips_for_service[(t.service_id, t.trip_headsign)].append(
                        TripInformation(
                            None,
                            None,
                            t.wheelchair_accessible,
                            t.bikes_allowed,
                            stops_for_trip,
                            t.trip_headsign
                        )
                    )
                    
                out.append(
                    RouteCanonicalServiceInformationV2(
                        r.id,
                        service_id,
                        [max(set(t), key=t.count) for t in trips_for_service.values()]
                    )
                )

        return out
