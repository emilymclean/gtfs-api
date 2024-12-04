from pathlib import Path
from typing import List, Dict, Callable

from .component.route_detail_generator import RouteDetailGeneratorComponent
from .component.service_list_generator import ServiceListGeneratorComponent
from .component.stop_detail_generator import StopDetailGeneratorComponent
from .component.stop_list_generator import StopListGeneratorComponent
from .component.intermediaries import StopCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV, StopTimeCSV, TripCSV
from .component.route_list_generator import RouteListGeneratorComponent
from .component.stop_timetable_generator import StopTimetableGeneratorComponent
from .models import *

T = TypeVar('T')

class Generator:

    def __init__(
            self,
            stop_csvs: List[GtfsCsv],
            route_csvs: List[GtfsCsv],
            calendar_csvs: List[GtfsCsv],
            calendar_date_csvs: List[GtfsCsv],
            shape_csvs: List[GtfsCsv],
            stop_time_csvs: List[GtfsCsv],
            trip_csvs: List[GtfsCsv],
    ):

        self.stop_data = [ParsedCsv[List[StopCSV]](StopCSV.from_csv(p.data), p.distinguisher) for p in stop_csvs]
        self.route_data = [ParsedCsv[List[RouteCSV]](RouteCSV.from_csv(p.data), p.distinguisher) for p in route_csvs]
        self.calendar_data = [ParsedCsv[List[CalendarCSV]](CalendarCSV.from_csv(p.data), p.distinguisher) for p in calendar_csvs]
        self.calendar_exception_data = [ParsedCsv[List[CalendarExceptionCSV]](CalendarExceptionCSV.from_csv(p.data), p.distinguisher) for p in calendar_date_csvs]
        self.stop_time_data = [ParsedCsv[List[StopTimeCSV]](StopTimeCSV.from_csv(p.data), p.distinguisher) for p in stop_time_csvs]
        self.trip_data = [ParsedCsv[List[TripCSV]](TripCSV.from_csv(p.data), p.distinguisher) for p in trip_csvs]

        self.stop_index = self._create_index(flatten_parsed(self.stop_data), lambda x: x.id)
        self.stop_index_by_parent = self._create_list_index(filter(lambda x: x.parent_station is not None, flatten_parsed(self.stop_data)), lambda x: x.parent_station)
        self.stop_time_index = self._create_list_index(flatten_parsed(self.stop_time_data), lambda x: x.stop_id)
        self.route_index = self._create_index(flatten_parsed(self.route_data), lambda x: x.id)
        self.trip_index = self._create_index(flatten_parsed(self.trip_data), lambda x: x.id)
        self.trip_index_by_service = self._create_list_index(flatten_parsed(self.trip_data), lambda x: x.service_id)
        self.calendar_index = self._create_list_index(flatten_parsed(self.calendar_data), lambda x: x.service_id)
        self.calendar_exception_index = self._create_list_index(flatten_parsed(self.calendar_exception_data), lambda x: x.service_id)

        self.distinguishers = list(filter(lambda x: x is not None, [d.distinguisher for d in route_csvs]))

    def generate(self, output_folder: Path):
        StopListGeneratorComponent(self.stop_data, self.distinguishers).generate(output_folder)
        StopDetailGeneratorComponent(self.stop_data, self.distinguishers).generate(output_folder)
        RouteListGeneratorComponent(self.route_data, self.distinguishers).generate(output_folder)
        RouteDetailGeneratorComponent(self.route_data, self.distinguishers).generate(output_folder)
        StopTimetableGeneratorComponent(
            self.stop_data,
            self.stop_time_index,
            self.stop_index_by_parent,
            self.trip_index,
            self.route_index,
            self.calendar_index,
            self.calendar_exception_index,
            self.distinguishers
        ).generate(output_folder)
        ServiceListGeneratorComponent(self.calendar_data, self.calendar_exception_index, self.trip_index_by_service, self.distinguishers).generate(output_folder)

    @staticmethod
    def _create_index(data: List[T], key: Callable[[T], str]) -> Dict[str, T]:
        out = {}
        for d in data:
            out[key(d)] = d
        return out

    @staticmethod
    def _create_list_index(data: List[T], key: Callable[[T], str]) -> Dict[str, List[T]]:
        out = {}
        for d in data:
            k = key(d)
            if k not in out:
                out[k] = [d]
            else:
                out[k].append(d)
        return out