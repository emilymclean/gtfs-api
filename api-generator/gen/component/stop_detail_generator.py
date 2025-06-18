from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any, Dict

from ..models import GtfsCsv, stops_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import StopCSV, StopIntermediary
from .. import format_pb2 as pb


@dataclass
class StopDetail:
    stop: StopIntermediary
    children: List[StopIntermediary]


class JsonStopDetailGeneratorFormat(JsonGeneratorFormat[StopDetail]):

    def parse(self, intermediary: StopDetail, distinguisher: Optional[str]) -> Any:
        return {
            'stop': intermediary.stop.to_json(),
            'children': [c.to_json() for c in intermediary.children],
        }


class ProtoStopDetailGeneratorFormat(ProtoGeneratorFormat[StopDetail]):

    def parse(self, intermediary: StopDetail, distinguisher: Optional[str]) -> Any:
        stop_detail = pb.StopDetailEndpoint()

        intermediary.stop.to_pb(stop_detail.stop)

        for c in intermediary.children:
            stop = pb.Stop()
            c.to_pb(stop)
            stop_detail.children.append(stop)

        return stop_detail


class StopDetailGeneratorComponent(FormatGeneratorComponent[StopDetail]):

    def __init__(
            self,
            stop_csvs: List[ParsedCsv[List[StopCSV]]],
            stop_index_by_parent: Dict[str, List[StopCSV]],
            distinguishers: List[str]
    ) -> None:
        self.csvs = stop_csvs
        self.stop_index_by_parent = stop_index_by_parent
        self.endpoint = stops_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[StopDetail]]:
        return [
            JsonStopDetailGeneratorFormat(),
            ProtoStopDetailGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: StopDetail, extension: str) -> Path:
        return output_folder.joinpath(f"v1/stop/{intermediary.stop.id}/details.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[StopDetail]:
        stops = flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))
        out = []

        for stop in stops:
            out.append(StopDetail(
                StopIntermediary.from_csv(stop, self.config),
                [
                    StopIntermediary.from_csv(x, self.config)
                    for x in (self.stop_index_by_parent[stop.id] if stop.id in self.stop_index_by_parent else [])
                ],
            ))

        return out
