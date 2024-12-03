from pathlib import Path
from typing import List, Optional, Any

from .consts import wheelchair_boarding_options_pb
from ..models import GtfsCsv, stops_endpoint
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import StopCSV, Intermediary
from .. import format_pb2 as pb


class StopTimeByStop(Intermediary):
    stop_id: str



class JsonStopTimesGeneratorFormat(JsonGeneratorFormat[List[StopCSV]]):

    def parse(self, intermediary: List[StopCSV], distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary]


class ProtoStopTimesGeneratorFormat(ProtoGeneratorFormat[List[StopCSV]]):

    def parse(self, intermediary: List[StopCSV], distinguisher: Optional[str]) -> Any:
        se = pb.StopEndpoint()
        for i in intermediary:
            stop = pb.Stop()
            stop.id = i.id
            stop.name = i.name

            stop.location.lat = i.location.lat
            stop.location.lng = i.location.lng

            stop.accessibility.wheelchair = wheelchair_boarding_options_pb[i.accessibility.wheelchair]
            se.stop.append(stop)

        return se


class StopTimesGeneratorComponent(FormatGeneratorComponent[List[StopCSV]]):

    def __init__(self, stops_csvs: List[GtfsCsv]):
        self.csvs = stops_csvs
        self.endpoint = stops_endpoint
        self.distinguishers = filter(lambda x: x is not None, [d.distinguisher for d in stops_csvs])

    def _formats(self) -> List[GeneratorFormat[List[StopCSV]]]:
        return [
            JsonStopTimesGeneratorFormat(),
            ProtoStopTimesGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: List[StopCSV], extension: str) -> Path:
        return output_folder.joinpath(f"stops.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[List[StopCSV]]:
        s = []
        csvs = filter(lambda x: x.distinguisher == distinguisher, self.csvs) if distinguisher is not None else self.csvs
        for csv in csvs:
            for i, r in csv.data.iterrows():
                s.append(StopCSV.from_csv_row(r))
        return [s]
