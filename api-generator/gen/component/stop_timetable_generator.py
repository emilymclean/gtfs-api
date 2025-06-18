from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Dict

from .consts import service_bikes_allowed, \
    service_wheelchair_accessible, service_bikes_allowed_pb
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import Intermediary, StopTimeCSV, TripCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV, StopCSV
from .. import format_pb2 as pb
from ..time_helper import TimeHelper


@dataclass
class StopTimeInformation(Intermediary):
    child_stop_id: Optional[str]
    route_id: str
    route_code: str
    service_id: str
    trip_id: str
    arrival_time: Any
    departure_time: Any
    heading: str
    sequence: int
    wheelchair_accessible: int
    bikes_allowed: int

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "child_stop_id": self.child_stop_id,
            "route_id": self.route_id,
            "route_code": self.route_code,
            "service_id": self.service_id,
            "trip_id": self.trip_id,
            "arrival_time": time_helper.output_time_iso(self.arrival_time),
            "departure_time": time_helper.output_time_iso(self.departure_time),
            "heading": self.heading,
            "sequence": self.sequence,
            "accessibility": {
                "bikesAllowed": service_bikes_allowed[self.bikes_allowed],
                "wheelchairAccessible": service_wheelchair_accessible[self.wheelchair_accessible],
            }
        }


@dataclass
class StopTimeByStop(Intermediary):
    stop_id: str
    times: List[StopTimeInformation]


class JsonStopTimesGeneratorFormat(JsonGeneratorFormat[StopTimeByStop]):

    def parse(self, intermediary: StopTimeByStop, distinguisher: Optional[str]) -> Any:
        return [i.to_json(self.time_helper) for i in intermediary.times]


class ProtoStopTimesGeneratorFormat(ProtoGeneratorFormat[StopTimeByStop]):

    def parse(self, intermediary: StopTimeByStop, distinguisher: Optional[str]) -> Any:
        out = pb.StopTimetable()

        for t in intermediary.times:
            time = pb.StopTimetableTime()
            if t.child_stop_id is not None:
                time.childStopId = t.child_stop_id
            time.routeId = t.route_id
            time.routeCode = t.route_code
            time.serviceId = t.service_id
            time.tripId = t.trip_id
            time.arrivalTime = self.time_helper.output_time_iso(t.arrival_time)
            time.departureTime = self.time_helper.output_time_iso(t.departure_time)
            time.heading = t.heading
            time.sequence = t.sequence

            time.accessibility.bikesAllowed = service_bikes_allowed_pb[t.bikes_allowed]
            time.accessibility.wheelchairAccessible = service_bikes_allowed_pb[t.wheelchair_accessible]

            out.times.append(time)

        return out


class StopTimetableGeneratorComponent(FormatGeneratorComponent[StopTimeByStop]):

    def __init__(
            self,
            stops: List[ParsedCsv[List[StopCSV]]],
            stop_time_index: Dict[str, List[StopTimeCSV]],
            stop_index_by_parent: Dict[str, List[StopCSV]],
            trip_index: Dict[str, TripCSV],
            route_index: Dict[str, RouteCSV],
            calendar_index: Dict[str, List[CalendarCSV]],
            calendar_exception_index: Dict[str, List[CalendarExceptionCSV]],
            distinguishers: List[str]
    ):
        self.stops = stops
        self.stop_time_index = stop_time_index
        self.stop_index_by_parent = stop_index_by_parent
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
        return output_folder.joinpath(f"v1/stop/{intermediary.stop_id}/timetable.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[StopTimeByStop]:
        stops = flatten_parsed(filter_parsed_by_distinguisher(self.stops, distinguisher))

        out = []
        for stop in stops:
            times = self._create_intermediary(None, [stop])
            out.append(StopTimeByStop(stop.id, times))

        return out

    def _create_intermediary(self, parent_id: Optional[str], stops: List[StopCSV]) -> List[StopTimeInformation]:
        out = []
        for s in stops:
            times = self.stop_time_index[s.id] if s.id in self.stop_time_index else []
            for t in times:
                trip = self.trip_index[t.trip_id]
                out.append(StopTimeInformation(
                    s.id if (s.id != parent_id) else None,
                    trip.route_id,
                    self.route_index[trip.route_id].code,
                    trip.service_id,
                    trip.id,
                    t.arrival_time,
                    t.departure_time,
                    trip.trip_headsign,
                    t.stop_sequence,
                    trip.wheelchair_accessible,
                    trip.bikes_allowed,
                ))

            children = self.stop_index_by_parent[s.id] if s.id in self.stop_index_by_parent else []
            if len(children) > 0:
                out.extend(self._create_intermediary(parent_id, children))

        return out
