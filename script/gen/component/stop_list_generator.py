from typing import List, Optional, Any

from .consts import wheelchair_boarding_options_pb
from ..models import stops_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat, \
    IndexedGeneratorComponent, IndexedWrapper
from .intermediaries import StopCSV
from .. import format_pb2 as pb


class JsonStopListGeneratorFormat(JsonGeneratorFormat[IndexedWrapper[StopCSV]]):

    def parse(self, intermediary: IndexedWrapper[StopCSV], distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary.data]


class ProtoStopListGeneratorFormat(ProtoGeneratorFormat[IndexedWrapper[StopCSV]]):

    def parse(self, intermediary: IndexedWrapper[StopCSV], distinguisher: Optional[str]) -> Any:
        se = pb.StopEndpoint()
        for i in intermediary.data:
            stop = pb.Stop()
            i.to_pb(stop)

            se.stop.append(stop)

        return se


class StopListGeneratorComponent(IndexedGeneratorComponent[IndexedWrapper[StopCSV]]):

    def __init__(self, stop_data: List[ParsedCsv[List[StopCSV]]], distinguishers: List[str]):
        self.csvs = stop_data
        self.endpoint = stops_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[IndexedWrapper[StopCSV]]]:
        return [
            JsonStopListGeneratorFormat(),
            ProtoStopListGeneratorFormat()
        ]

    def _name(self) -> str:
        return "stops"

    def _read_all_intermediary(self, distinguisher: Optional[str]) -> List[StopCSV]:
        return flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))

    def _keys_from_intermediary(self, intermediary: StopCSV) -> List[str]:
        return [intermediary.id, intermediary.name]

