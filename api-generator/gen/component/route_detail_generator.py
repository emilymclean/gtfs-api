from pathlib import Path
from typing import List, Optional, Any

from .consts import route_type_options_pb
from ..models import GtfsCsv, routes_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import RouteCSV, RouteIntermediary
from .. import format_pb2 as pb


class JsonRouteDetailGeneratorFormat(JsonGeneratorFormat[RouteIntermediary]):

    def parse(self, intermediary: RouteIntermediary, distinguisher: Optional[str]) -> Any:
        return {
            'route': intermediary.to_json()
        }


class ProtoRouteDetailGeneratorFormat(ProtoGeneratorFormat[RouteIntermediary]):

    def parse(self, intermediary: RouteIntermediary, distinguisher: Optional[str]) -> Any:
        route_detail = pb.RouteDetailEndpoint()
        intermediary.to_pb(route_detail.route)
        return route_detail


class RouteDetailGeneratorComponent(FormatGeneratorComponent[RouteIntermediary]):

    def __init__(self, route_csvs: List[ParsedCsv[List[RouteCSV]]], distinguishers: List[str]) -> None:
        self.csvs = route_csvs
        self.endpoint = routes_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[RouteIntermediary]]:
        return [
            JsonRouteDetailGeneratorFormat(),
            ProtoRouteDetailGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteIntermediary, extension: str) -> Path:
        return output_folder.joinpath(f"v1/route/{intermediary.id}/details.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteIntermediary]:
        return [
            RouteIntermediary.from_csv(x, self.config)
            for x in flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))
        ]
