from pathlib import Path
from typing import List, Optional, Any

from .consts import route_type_options_pb
from ..models import GtfsCsv, routes_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import RouteCSV
from .. import format_pb2 as pb


class JsonRouteDetailGeneratorFormat(JsonGeneratorFormat[RouteCSV]):

    def parse(self, intermediary: RouteCSV, distinguisher: Optional[str]) -> Any:
        return {
            'route': intermediary.to_json()
        }


class ProtoRouteDetailGeneratorFormat(ProtoGeneratorFormat[RouteCSV]):

    def parse(self, intermediary: RouteCSV, distinguisher: Optional[str]) -> Any:
        route_detail = pb.RouteDetailEndpoint()
        route_detail.route.id = intermediary.id
        route_detail.route.code = intermediary.code
        route_detail.route.name = intermediary.name
        route_detail.route.type = route_type_options_pb[intermediary.type]

        return route_detail


class RouteDetailGeneratorComponent(FormatGeneratorComponent[RouteCSV]):

    def __init__(self, route_csvs: List[ParsedCsv[List[RouteCSV]]], distinguishers: List[str]) -> None:
        self.csvs = route_csvs
        self.endpoint = routes_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[RouteCSV]]:
        return [
            JsonRouteDetailGeneratorFormat(),
            ProtoRouteDetailGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteCSV, extension: str) -> Path:
        return output_folder.joinpath(f"route/{intermediary.id}/details.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteCSV]:
        return flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))
