from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import strptime
from typing import List, Optional, Any, Dict

from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV
from .. import format_pb2 as pb


@dataclass
class RouteServiceInformation(Intermediary):
    route_id: str
    service_ids: List[str]

    def to_json(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "service_ids": self.service_ids,
        }


class JsonRouteServiceGeneratorFormat(JsonGeneratorFormat[RouteServiceInformation]):

    def parse(self, intermediary: RouteServiceInformation, distinguisher: Optional[str]) -> Any:
        return intermediary.to_json()


class ProtoRouteServiceGeneratorFormat(ProtoGeneratorFormat[RouteServiceInformation]):

    def parse(self, intermediary: RouteServiceInformation, distinguisher: Optional[str]) -> Any:
        out = pb.RouteServicesEndpoint()

        for s in intermediary.service_ids:
            out.serviceIds.append(s)

        return out


class RouteServiceGeneratorComponent(FormatGeneratorComponent[RouteServiceInformation]):

    def __init__(
            self,
            route_data: List[ParsedCsv[List[RouteCSV]]],
            trip_index_by_route: Dict[str, List[TripCSV]],
            distinguishers: List[str]
    ):
        self.route_data = route_data
        self.trip_index_by_route = trip_index_by_route
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[RouteServiceInformation]]:
        return [
            JsonRouteServiceGeneratorFormat(),
            ProtoRouteServiceGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: RouteServiceInformation, extension: str) -> Path:
        return output_folder.joinpath(f"route/{intermediary.route_id}/services.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[RouteServiceInformation]:
        routes = flatten_parsed(filter_parsed_by_distinguisher(self.route_data, distinguisher))
        return self._create_intermediary(routes)

    def _create_intermediary(self, routes: List[RouteCSV]) -> List[RouteServiceInformation]:
        out = []
        for r in routes:
            trips = self.trip_index_by_route[r.id] if r.id in self.trip_index_by_route else None
            if trips is None:
                out.append(RouteServiceInformation(r.id, []))
                continue

            services = []
            for t in trips:
                if t.service_id in services:
                    continue
                services.append(t.service_id)

            out.append(RouteServiceInformation(r.id, services))

        return out
