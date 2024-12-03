from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any, Dict

from .consts import wheelchair_boarding_options_pb
from ..models import GtfsCsv, stops_endpoint, ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV
from .. import format_pb2 as pb


@dataclass
class StopTimeInformation(Intermediary):
    route_id: str
    arrival_time: str
    departure_time: str
    heading: str
    sequence: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "arrival_time": self.arrival_time,
            "departure_time": self.departure_time,
            "heading": self.heading,
            "sequence": self.sequence,
        }


@dataclass
class StopTimeByStop(Intermediary):
    stop_id: str
    times: List[StopTimeInformation]


class JsonStopTimesGeneratorFormat(JsonGeneratorFormat[StopTimeByStop]):

    def parse(self, intermediary: StopTimeByStop, distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary.times]


# class ProtoStopTimesGeneratorFormat(ProtoGeneratorFormat[List[StopCSV]]):
#
#     def parse(self, intermediary: List[StopCSV], distinguisher: Optional[str]) -> Any:
#         se = pb.StopEndpoint()
#         for i in intermediary:
#             stop = pb.Stop()
#             stop.id = i.id
#             stop.name = i.name
#
#             stop.location.lat = i.location.lat
#             stop.location.lng = i.location.lng
#
#             stop.accessibility.wheelchair = wheelchair_boarding_options_pb[i.accessibility.wheelchair]
#             se.stop.append(stop)
#
#         return se


class StopTimesGeneratorComponent(FormatGeneratorComponent[StopTimeByStop]):

    def __init__(
            self,
            stop_times: List[ParsedCsv[List[StopTimeCSV]]],
            trip_index: Dict[str, TripCSV]
    ):
        self.stop_times = stop_times
        self.trip_index = trip_index
        self.distinguishers = filter(lambda x: x is not None, [d.distinguisher for d in stop_times])

    def _formats(self) -> List[GeneratorFormat[StopTimeByStop]]:
        return [
            JsonStopTimesGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: StopTimeByStop, extension: str) -> Path:
        return output_folder.joinpath(f"stop/{intermediary.stop_id}/timetable.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[StopTimeByStop]:
        stop_times = flatten_parsed(filter_parsed_by_distinguisher(self.stop_times, distinguisher))

        return self._create_intermediary(stop_times)

    def _create_intermediary(self, stop_times: List[StopTimeCSV]) -> List[StopTimeByStop]:
        stop_ids = list(set([s.stop_id for s in stop_times]))
        times_by_stop = {key: [] for key in stop_ids}
        for t in stop_times:
            times_by_stop[t.stop_id].append(t)

        out = []
        for s, f_times in times_by_stop.items():
            print(f"Creating stop times for stop {s}")
            i_times = []
            for t in f_times:
                trip = self.trip_index[t.trip_id]
                i_times.append(StopTimeInformation(
                    trip.route_id,
                    t.arrival_time,
                    t.departure_time,
                    trip.trip_headsign,
                    t.stop_sequence
                ))

            out.append(StopTimeByStop(
                s,
                i_times,
            ))

        return out
