from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any

from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import RouteCSV, TripCSV, StopTimeCSV, StopCSV
from .. import trip_index_pb2 as pb
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed


@dataclass
class TripInformation:
    trip_id: str
    route_id: str
    stop_ids: List[str]


@dataclass
class TripIndexIntermediary:
    information: List[TripInformation]


class JsonTripIndexGeneratorFormat(JsonGeneratorFormat[TripIndexIntermediary]):

    def parse(self, intermediary: TripIndexIntermediary, distinguisher: Optional[str]) -> Any:
        return {
            'route': intermediary.to_json()
        }


class ProtoTripIndexGeneratorFormat(ProtoGeneratorFormat[TripIndexIntermediary]):

    def parse(self, intermediary: TripIndexIntermediary, distinguisher: Optional[str]) -> Any:
        index = pb.TripIndex()

        for trip in intermediary.information:
            info = pb.TripInformation()

            info.tripId = trip.trip_id
            info.routeId = trip.route_id
            info.stopIds.extend(trip.stop_ids)

            index.trips.append(info)

        return index


class TripIndexGeneratorComponent(FormatGeneratorComponent[TripIndexIntermediary]):

    def __init__(
            self,
            trip_data: List[ParsedCsv[List[TripCSV]]],
            route_index: dict[str, RouteCSV],
            stop_time_index_by_trip: dict[str, List[StopTimeCSV]],
            stop_index: dict[str, StopCSV],
            distinguishers: List[str]
    ) -> None:
        self.trip_data = trip_data
        self.route_index = route_index
        self.stop_time_index_by_trip = stop_time_index_by_trip
        self.stop_index = stop_index
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[TripIndexIntermediary]]:
        return [
            ProtoTripIndexGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: TripIndexIntermediary, extension: str) -> Path:
        return output_folder.joinpath(f"trip-index.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[TripIndexIntermediary]:
        return [TripIndexIntermediary(
            [
                TripInformation(
                    t.id,
                    t.route_id,
                    list(
                        {
                            xs
                            for s in self.stop_time_index_by_trip[t.id]
                            for xs in self._stops_and_parents(s.stop_id)
                        }
                    )
                )
                for t in flatten_parsed(filter_parsed_by_distinguisher(self.trip_data, distinguisher))
            ]
        )]

    def _stops_and_parents(self, stop_id: str) -> List[str]:
        out = [stop_id]
        parent = self.stop_index[stop_id].parent_station

        if parent is not None:
            out += self._stops_and_parents(parent)

        return out
