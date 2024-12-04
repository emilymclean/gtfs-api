from pathlib import Path
from typing import List, Optional, Any

from .consts import wheelchair_boarding_options_pb
from ..models import GtfsCsv, stops_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import StopCSV
from .. import format_pb2 as pb


class JsonStopDetailGeneratorFormat(JsonGeneratorFormat[StopCSV]):

    def parse(self, intermediary: StopCSV, distinguisher: Optional[str]) -> Any:
        return {
            'stop': intermediary.to_json()
        }


class ProtoStopDetailGeneratorFormat(ProtoGeneratorFormat[StopCSV]):

    def parse(self, intermediary: StopCSV, distinguisher: Optional[str]) -> Any:
        stop_detail = pb.StopDetailEndpoint()

        stop_detail.stop.id = intermediary.id
        stop_detail.stop.name = intermediary.name

        stop_detail.stop.location.lat = intermediary.location.lat
        stop_detail.stop.location.lng = intermediary.location.lng

        stop_detail.stop.accessibility.stopWheelchairAccessible = wheelchair_boarding_options_pb[intermediary.accessibility.wheelchair]

        return stop_detail


class StopDetailGeneratorComponent(FormatGeneratorComponent[StopCSV]):

    def __init__(self, stop_csvs: List[ParsedCsv[List[StopCSV]]], distinguishers: List[str]) -> None:
        self.csvs = stop_csvs
        self.endpoint = stops_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[StopCSV]]:
        return [
            JsonStopDetailGeneratorFormat(),
            ProtoStopDetailGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: StopCSV, extension: str) -> Path:
        return output_folder.joinpath(f"stop/{intermediary.id}/details.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[StopCSV]:
        return flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))
