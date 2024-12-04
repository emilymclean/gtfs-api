from typing import List, Optional, Any

from ..models import routes_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat, \
    IndexedGeneratorComponent, IndexedWrapper, T
from .intermediaries import RouteCSV, RouteIntermediary
from .. import format_pb2 as pb


class JsonRouteListGeneratorFormat(JsonGeneratorFormat[IndexedWrapper[RouteIntermediary]]):

    def parse(self, intermediary: IndexedWrapper[RouteIntermediary], distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary.data]


class ProtoRouteListGeneratorFormat(ProtoGeneratorFormat[IndexedWrapper[RouteIntermediary]]):

    def parse(self, intermediary: IndexedWrapper[RouteIntermediary], distinguisher: Optional[str]) -> Any:
        re = pb.RouteEndpoint()
        for i in intermediary.data:
            route = pb.Route()
            i.to_pb(route)
            re.route.append(route)

        return re


class RouteListGeneratorComponent(IndexedGeneratorComponent[RouteIntermediary]):

    def __init__(self, route_csvs: List[ParsedCsv[List[RouteCSV]]], distinguishers: List[str]) -> None:
        self.csvs = route_csvs
        self.endpoint = routes_endpoint
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[IndexedWrapper[RouteIntermediary]]]:
        return [
            JsonRouteListGeneratorFormat(),
            ProtoRouteListGeneratorFormat()
        ]

    def _name(self) -> str:
        return "routes"

    def _read_all_intermediary(self, distinguisher: Optional[str]) -> List[RouteIntermediary]:
        return [
            RouteIntermediary.from_csv(x, self.config)
            for x in flatten_parsed(filter_parsed_by_distinguisher(self.csvs, distinguisher))
        ]

    def _keys_from_intermediary(self, intermediary: RouteIntermediary) -> List[str]:
        return [intermediary.name, intermediary.code]


