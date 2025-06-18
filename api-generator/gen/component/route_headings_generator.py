from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any, Dict

from .consts import route_type_options_pb
from ..models import GtfsCsv, routes_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import RouteCSV, RouteIntermediary, TripCSV, Intermediary
from .. import format_pb2 as pb


@dataclass
class RouteHeadingInformation(Intermediary):
    route_id: str
    headings: List[str]

    def to_json(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "headings": self.headings,
        }


class JsonRouteHeadingsGeneratorFormat(JsonGeneratorFormat[RouteHeadingInformation]):

    def parse(self, intermediary: RouteHeadingInformation, distinguisher: Optional[str]) -> Any:
        return intermediary.to_json()


class ProtoRouteHeadingsGeneratorFormat(ProtoGeneratorFormat[RouteHeadingInformation]):

    def parse(self, intermediary: RouteHeadingInformation, distinguisher: Optional[str]) -> Any:
        out = pb.RouteHeadingsEndpoint()

        for s in intermediary.headings:
            out.headings.append(s)

        return out


class RouteHeadingsGeneratorComponent(FormatGeneratorComponent[RouteHeadingInformation]):

    def __init__(
            self,
            route_csvs: List[ParsedCsv[List[RouteCSV]]],
            trip_index_by_route: Dict[str, List[TripCSV]],
            distinguishers: List[str]
    ) -> None:
        self.route_csvs = route_csvs
        self.trip_index_by_route = trip_index_by_route
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[RouteHeadingInformation]]:
        return [
            JsonRouteHeadingsGeneratorFormat(),
            ProtoRouteHeadingsGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteHeadingInformation, extension: str) -> Path:
        return output_folder.joinpath(f"v1/route/{intermediary.route_id}/headings.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteHeadingInformation]:
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.route_csvs, distinguisher))
        return self._create_intermediary(routes)

    def _create_intermediary(self, routes: List[RouteCSV]) -> List[RouteHeadingInformation]:
        out = []
        for r in routes:
            trips = self.trip_index_by_route[r.id] if r.id in self.trip_index_by_route else None
            if trips is None:
                out.append(RouteHeadingInformation(r.id, []))
                continue

            headings = []
            for t in trips:
                if t.service_id in headings:
                    continue
                headings.append(t.trip_headsign)

            out.append(RouteHeadingInformation(r.id, list(set(headings))))

        return out
