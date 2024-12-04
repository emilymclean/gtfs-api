from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any

from .consts import route_type_options_pb
from ..models import GtfsCsv, routes_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import RouteCSV, StopCSV
from .. import format_pb2 as pb


@dataclass
class IndexableRouteList:
    index: Optional[str]
    routes: List[RouteCSV]


class JsonRouteListGeneratorFormat(JsonGeneratorFormat[IndexableRouteList]):

    def parse(self, intermediary: IndexableRouteList, distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary.routes]


class ProtoRouteListGeneratorFormat(ProtoGeneratorFormat[IndexableRouteList]):

    def parse(self, intermediary: IndexableRouteList, distinguisher: Optional[str]) -> Any:
        re = pb.RouteEndpoint()
        for i in intermediary.routes:
            route = pb.Route()
            i.to_pb(route)
            re.route.append(route)

        return re


class RouteListGeneratorComponent(FormatGeneratorComponent[IndexableRouteList]):

    def __init__(self, route_csvs: List[ParsedCsv[List[RouteCSV]]], distinguishers: List[str]) -> None:
        self.csvs = route_csvs
        self.endpoint = routes_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[IndexableRouteList]]:
        return [
            JsonRouteListGeneratorFormat(),
            ProtoRouteListGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: IndexableRouteList, extension: str) -> Path:
        if intermediary.index is None:
            return output_folder.joinpath(f"routes.{extension}")
        else:
            return output_folder.joinpath(f"index/routes/{intermediary.index}/routes.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[IndexableRouteList]:
        idx = {key: [] for key in "abcdefghijklmnopqrstuvwxyz0123456789"}
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))

        for route in routes:
            keys = {route.code[0].lower(), route.name[0].lower()}
            for k in keys:
                idx[k].append(route)

        indexed = [IndexableRouteList(k, v) for k, v in idx.items()]
        indexed.append(IndexableRouteList(None, routes))

        return indexed
