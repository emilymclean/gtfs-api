from dataclasses import dataclass
from pathlib import Path
from time import strptime
from typing import List, Optional, Any, Dict

from .consts import gt_date_format, timetable_service_exception_type_pb, parse_datetime
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV
from .. import format_pb2 as pb


@dataclass
class StopTimeInformation(Intermediary):
    route_id: str
    route_code: str
    service_id: str
    arrival_time: str
    departure_time: str
    heading: str
    sequence: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "route_code": self.route_code,
            "service_id": self.service_id,
            "arrival_time": self.arrival_time,
            "departure_time": self.departure_time,
            "heading": self.heading,
            "sequence": self.sequence
        }


@dataclass
class StopTimeByStop(Intermediary):
    stop_id: str
    times: List[StopTimeInformation]


class JsonStopTimesGeneratorFormat(JsonGeneratorFormat[StopTimeByStop]):

    def parse(self, intermediary: StopTimeByStop, distinguisher: Optional[str]) -> Any:
        return [i.to_json() for i in intermediary.times]


class ProtoStopTimesGeneratorFormat(ProtoGeneratorFormat[StopTimeByStop]):

    def parse(self, intermediary: StopTimeByStop, distinguisher: Optional[str]) -> Any:
        out = pb.StopTimetable()

        for t in intermediary.times:
            time = pb.StopTimetableTime()
            time.routeId = t.route_id
            time.routeCode = t.route_code
            time.serviceId = t.service_id
            time.arrivalTime = t.arrival_time
            time.departureTime = t.departure_time
            time.heading = t.heading
            time.sequence = t.sequence

            out.times.append(time)

        return out


class StopTimesGeneratorComponent(FormatGeneratorComponent[StopTimeByStop]):

    def __init__(
            self,
            stop_times: List[ParsedCsv[List[StopTimeCSV]]],
            trip_index: Dict[str, TripCSV],
            route_index: Dict[str, RouteCSV],
            calendar_index: Dict[str, List[CalendarCSV]],
            calendar_exception_index: Dict[str, List[CalendarExceptionCSV]],
            distinguishers: List[str]
    ):
        self.stop_times = stop_times
        self.trip_index = trip_index
        self.route_index = route_index
        self.calendar_index = calendar_index
        self.calendar_exception_index = calendar_exception_index
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[StopTimeByStop]]:
        return [
            JsonStopTimesGeneratorFormat(),
            ProtoStopTimesGeneratorFormat()
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
                    self.route_index[trip.route_id].code,
                    trip.service_id,
                    t.arrival_time,
                    t.departure_time,
                    trip.trip_headsign,
                    t.stop_sequence,
                    self.calendar_index[trip.service_id] if trip.service_id in self.calendar_index else [],
                    self.calendar_exception_index[trip.service_id] if trip.service_id in self.calendar_exception_index else [],
                ))

            out.append(StopTimeByStop(
                s,
                i_times,
            ))

        return out
