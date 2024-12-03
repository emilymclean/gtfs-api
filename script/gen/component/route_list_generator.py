from pathlib import Path
from typing import List, Optional, Any

from .consts import route_type_options_pb
from ..models import GtfsCsv, routes_endpoint, ParsedCsv
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import RouteCSV
from .. import format_pb2 as pb


class JsonRouteListGeneratorFormat(JsonGeneratorFormat[List[RouteCSV]]):

    def parse(self, intermediary: List[RouteCSV], distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary]


class ProtoRouteListGeneratorFormat(ProtoGeneratorFormat[List[RouteCSV]]):

    def parse(self, intermediary: List[RouteCSV], distinguisher: Optional[str]) -> Any:
        re = pb.RouteEndpoint()
        for i in intermediary:
            route = pb.Route()
            route.id = i.id
            route.code = i.code
            route.name = i.name
            route.type = route_type_options_pb[i.type]

            re.route.append(route)

        return re


class RouteListGeneratorComponent(FormatGeneratorComponent[List[RouteCSV]]):

    def __init__(self, route_csvs: List[ParsedCsv[List[RouteCSV]]]):
        self.csvs = route_csvs
        self.endpoint = routes_endpoint
        self.distinguishers = filter(lambda x: x is not None, [d.distinguisher for d in route_csvs])

    def _formats(self) -> List[GeneratorFormat[List[RouteCSV]]]:
        return [
            JsonRouteListGeneratorFormat(),
            ProtoRouteListGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: List[RouteCSV], extension: str) -> Path:
        return output_folder.joinpath(f"routes.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[List[RouteCSV]]:
        s = []
        csvs = filter(lambda x: x.distinguisher == distinguisher, self.csvs) if distinguisher is not None else self.csvs
        for csv in csvs:
            s.extend(csv.data)
        return [s]
