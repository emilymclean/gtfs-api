from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any, Dict

from ..models import GtfsCsv, stops_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import StopCSV, StopIntermediary, StopTimeCSV, TripCSV
from .. import format_pb2 as pb


@dataclass
class StopRoutes:
    stop_id: str
    route_ids: List[str]

    def to_json(self) -> Dict[str, Any]:
        return {
            "stop_id": self.stop_id,
            "route_ids": self.route_ids,
        }


class JsonStopRoutesGeneratorFormat(JsonGeneratorFormat[StopRoutes]):

    def parse(self, intermediary: StopRoutes, distinguisher: Optional[str]) -> Any:
        return intermediary.to_json()


class ProtoStopRoutesGeneratorFormat(ProtoGeneratorFormat[StopRoutes]):

    def parse(self, intermediary: StopRoutes, distinguisher: Optional[str]) -> Any:
        out = pb.StopRoutesEndpoint()

        for s in intermediary.route_ids:
            out.routeIds.append(s)

        return out


class StopRoutesGeneratorComponent(FormatGeneratorComponent[StopRoutes]):

    def __init__(
            self,
            stop_time_data: List[ParsedCsv[List[StopTimeCSV]]],
            trip_index: Dict[str, TripCSV],
            distinguishers: List[str]
    ) -> None:
        self.stop_time_data = stop_time_data
        self.trip_index = trip_index
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[StopRoutes]]:
        return [
            JsonStopRoutesGeneratorFormat(),
            ProtoStopRoutesGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: StopRoutes, extension: str) -> Path:
        return output_folder.joinpath(f"v1/stop/{intermediary.stop_id}/routes.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[StopRoutes]:
        stop_times = flatten_parsed(filter_parsed_by_distinguisher(self.stop_time_data, distinguisher))
        stops = {}

        for stop_time in stop_times:
            if stop_time.stop_sequence > 1:
                continue

            stops[stop_time.stop_id] = ((stops[stop_time.stop_id] if stop_time.stop_id in stops else set()) |
                                        {self.trip_index[stop_time.trip_id].route_id})

        out = [
            StopRoutes(k, list(v))
            for k, v in stops.items()
        ]

        return out
