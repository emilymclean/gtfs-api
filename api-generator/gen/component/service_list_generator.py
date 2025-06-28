from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any, Dict

from .consts import timetable_service_exception_type_pb, \
    service_bikes_allowed, service_wheelchair_accessible, service_bikes_allowed_pb
from ..models import ParsedCsv, filter_parsed_by_distinguisher, flatten_parsed
from .base import FormatGeneratorComponent, GeneratorFormat, JsonGeneratorFormat, ProtoGeneratorFormat
from .intermediaries import CalendarCSV, CalendarExceptionCSV, TripCSV
from .. import format_pb2 as pb
from ..time_helper import TimeHelper


@dataclass
class ServiceIntermediary:
    service_id: str
    calendar: List[CalendarCSV]
    exceptions: List[CalendarExceptionCSV]
    bikes_allowed: int
    all_trips_bikes_allowed: bool
    wheelchair_accessible: int
    all_trips_wheelchair_accessible: bool

    def to_json(self, time_helper: TimeHelper) -> Dict[str, Any]:
        return {
            "id": self.service_id,
            "regular": [c.to_json(time_helper) for c in self.calendar],
            "exception": [c.to_json(time_helper) for c in self.exceptions],
            "accessibility": {
                "bikesAllowed": service_bikes_allowed[self.bikes_allowed],
                "bikesAllowedAppliesToAllTrips": self.all_trips_bikes_allowed,
                "wheelchairAccessible": service_wheelchair_accessible[self.wheelchair_accessible],
                "wheelchairAccessibleAppliesToAllTrips": self.all_trips_wheelchair_accessible,
            }
        }


class JsonServiceListGeneratorFormat(JsonGeneratorFormat[List[ServiceIntermediary]]):

    def parse(self, intermediary: List[ServiceIntermediary], distinguisher: Optional[str]) -> Any:
        return [i.to_json(self.time_helper) for i in intermediary]


class ProtoServiceListGeneratorFormat(ProtoGeneratorFormat[List[ServiceIntermediary]]):

    def parse(self, intermediary: List[ServiceIntermediary], distinguisher: Optional[str]) -> Any:
        out = pb.ServiceEndpoint()
        for i in intermediary:
            service = pb.Service()
            service.id = i.service_id

            for c in i.calendar:
                regular = pb.TimetableServiceRegular()
                regular.monday = c.days_of_week[0]
                regular.tuesday = c.days_of_week[1]
                regular.wednesday = c.days_of_week[2]
                regular.thursday = c.days_of_week[3]
                regular.friday = c.days_of_week[4]
                regular.saturday = c.days_of_week[5]
                regular.sunday = c.days_of_week[6]
                regular.startDate = self.time_helper.output_date_iso(c.start_date)
                regular.endDate = self.time_helper.output_date_iso(c.end_date)
                service.regular.append(regular)

            for c in i.exceptions:
                exception = pb.TimetableServiceException()
                exception.date = self.time_helper.output_date_iso(c.date)
                exception.type = timetable_service_exception_type_pb[c.type]
                service.exception.append(exception)

            service.accessibility.bikesAllowed = service_bikes_allowed_pb[i.bikes_allowed]
            service.accessibility.bikesAllowedAppliesToAllTrips = i.all_trips_bikes_allowed
            service.accessibility.wheelchairAccessible = service_bikes_allowed_pb[i.wheelchair_accessible]
            service.accessibility.wheelchairAccessibleAppliesToAllTrips = i.all_trips_wheelchair_accessible

            out.service.append(service)

        return out


class ServiceListGeneratorComponent(FormatGeneratorComponent[List[ServiceIntermediary]]):

    def __init__(
            self,
            calendar_data: List[ParsedCsv[List[CalendarCSV]]],
            exception_index: Dict[str, List[CalendarExceptionCSV]],
            trip_index_by_service: Dict[str, List[TripCSV]],
            distinguishers: List[str]
    ) -> None:
        self.calendar_data = calendar_data
        self.exception_index = exception_index
        self.trip_index_by_service = trip_index_by_service
        self.distinguishers = distinguishers

    def _formats(self) -> List[GeneratorFormat[List[ServiceIntermediary]]]:
        return [
            JsonServiceListGeneratorFormat(),
            ProtoServiceListGeneratorFormat()
        ]

    def _path(self, output_folder: Path, intermediary: List[ServiceIntermediary], extension: str) -> Path:
        return output_folder.joinpath(f"v1/services.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[List[ServiceIntermediary]]:
        calendar = flatten_parsed(filter_parsed_by_distinguisher(self.calendar_data, distinguisher))

        out = []
        for c in calendar:
            exceptions = self.exception_index[c.service_id] if c.service_id in self.exception_index else []
            trips = self.trip_index_by_service[c.service_id] if c.service_id in self.trip_index_by_service else []

            if len(trips) > 0:
                accessibility_counts = [{0: 0, 1: 0, 2: 0}, {0: 0, 1: 0, 2: 0}]

                for trip in trips:
                    accessibility_counts[0][trip.wheelchair_accessible] += 1
                    accessibility_counts[1][trip.bikes_allowed] += 1

                selected = []
                applies_to_all = []
                for a in accessibility_counts:
                    opt = 1 if a[1] > 0 else 2 if a[2] > 0 else 0
                    selected.append(opt)
                    applies_to_all.append(a[opt] == len(trips))
            else:
                selected = [0, 0]
                applies_to_all = [True, True]

            out.append(ServiceIntermediary(
                c.service_id,
                [c],
                exceptions,
                selected[1],
                applies_to_all[1],
                selected[0],
                applies_to_all[0],
            ))

        return [out]