from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any

from .consts import wheelchair_boarding_options_pb
from ..models import stops_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import StopCSV
from .. import format_pb2 as pb


@dataclass
class IndexableStopList:
    index: Optional[str]
    stops: List[StopCSV]


class JsonStopListGeneratorFormat(JsonGeneratorFormat[IndexableStopList]):

    def parse(self, intermediary: IndexableStopList, distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary.stops]


class ProtoStopListGeneratorFormat(ProtoGeneratorFormat[IndexableStopList]):

    def parse(self, intermediary: IndexableStopList, distinguisher: Optional[str]) -> Any:
        se = pb.StopEndpoint()
        for i in intermediary.stops:
            stop = pb.Stop()
            i.to_pb(stop)

            se.stop.append(stop)

        return se


class StopListGeneratorComponent(FormatGeneratorComponent[IndexableStopList]):

    def __init__(self, stop_data: List[ParsedCsv[List[StopCSV]]], distinguishers: List[str]):
        self.csvs = stop_data
        self.endpoint = stops_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[IndexableStopList]]:
        return [
            JsonStopListGeneratorFormat(),
            ProtoStopListGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: IndexableStopList, extension: str) -> Path:
        if intermediary.index is None:
            return output_folder.joinpath(f"stops.{extension}")
        else:
            return output_folder.joinpath(f"index/stops/{intermediary.index}/stops.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[IndexableStopList]:
        idx = {key: [] for key in "abcdefghijklmnopqrstuvwxyz0123456789"}
        stops = flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))

        for stop in stops:
            keys = {stop.id[0].lower(), stop.name[0].lower()}
            for k in keys:
                idx[k].append(stop)

        indexed = [IndexableStopList(k, v) for k, v in idx.items()]
        indexed.append(IndexableStopList(None, stops))

        return indexed
