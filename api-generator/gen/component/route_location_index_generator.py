from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .. import format_pb2 as pb
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import LocationCSV, StopCSV, StopTimeCSV, TripCSV


@dataclass
class RouteLocationIndex:
    point: LocationCSV
    route_ids: List[str]

    def to_json(self) -> Dict[str, Any]:
        return {
            "point": self.point.to_json(),
            "route_id": self.route_ids,
        }


class ProtoRouteLocationIndexGeneratorFormat(ProtoGeneratorFormat[List[RouteLocationIndex]]):

    def parse(self, intermediary: List[RouteLocationIndex], distinguisher: Optional[str]) -> Any:
        out = pb.RouteLocationIndexEndpoint()
        for i in intermediary:
            index = out.indicies.add()
            index.point.lat = i.point.lat
            index.point.lng = i.point.lng
            index.routeId.extend(i.route_ids)
        return out


class RouteLocationIndexGeneratorComponent(FormatGeneratorComponent[List[RouteLocationIndex]]):

    def __init__(
            self,
            stop_csvs: List[ParsedCsv[List[StopCSV]]],
            stop_time_data: List[ParsedCsv[List[StopTimeCSV]]],
            trip_index: Dict[str, TripCSV],
            distinguishers: List[str]
    ) -> None:
        self.stop_csvs = stop_csvs
        self.stop_time_data = stop_time_data
        self.trip_index = trip_index
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[List[RouteLocationIndex]]]:
        return [
            ProtoRouteLocationIndexGeneratorFormat(),
        ]

    def _path(self, output_folder: Path, intermediary: List[RouteLocationIndex], extension: str) -> Path:
        return output_folder.joinpath(f"v1/route/location-index.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[List[RouteLocationIndex]]:
        stops = flatten_parsed(filter_parsed_by_distinguisher(self.stop_csvs, distinguisher))
        stop_times = flatten_parsed(filter_parsed_by_distinguisher(self.stop_time_data, distinguisher))

        routes_by_stop: Dict[str, set[str]] = {}
        for stop_time in stop_times:
            trip = self.trip_index.get(stop_time.trip_id)
            if trip is not None:
                routes_by_stop.setdefault(stop_time.stop_id, set()).add(trip.route_id)

        return [[
            RouteLocationIndex(
                stop.location,
                sorted(routes_by_stop.get(stop.id, set())),
            )
            for stop in stops
        ]]
