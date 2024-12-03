from pathlib import Path
from typing import List

from .component.stop_list_generator import StopListGeneratorComponent
from .component.intermediaries import StopCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV, StopTimeCSV, TripCSV
from .component.route_list_generator import RouteListGeneratorComponent
from .component.stop_times_generator import StopTimesGeneratorComponent
from .models import *


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
        self.stop_csvs = stop_csvs
        self.route_csvs = route_csvs
        # self.calendar_csvs = calendar_csvs
        # self.calendar_exception_csvs = [ParsedCsv[List[CalendarExceptionCSV]](CalendarExceptionCSV.from_csv(p.data), p.distinguisher) for p in calendar_date_csvs]
        self.stop_time_csvs = stop_time_csvs
        self.trip_csvs = trip_csvs

        self.stop_data = [ParsedCsv[List[StopCSV]](StopCSV.from_csv(p.data), p.distinguisher) for p in stop_csvs]
        self.route_data = [ParsedCsv[List[RouteCSV]](RouteCSV.from_csv(p.data), p.distinguisher) for p in route_csvs]
        # self.calendar_data = [ParsedCsv[List[CalendarCSV]](CalendarCSV.from_csv(p.data), p.distinguisher) for p in calendar_csvs]
        # self.calendar_exception_data = [ParsedCsv[List[CalendarExceptionCSV]](CalendarExceptionCSV.from_csv(p.data), p.distinguisher) for p in calendar_date_csvs]
        self.stop_time_data = [ParsedCsv[List[StopTimeCSV]](StopTimeCSV.from_csv(p.data), p.distinguisher) for p in stop_time_csvs]
        self.trip_data = [ParsedCsv[List[TripCSV]](TripCSV.from_csv(p.data), p.distinguisher) for p in trip_csvs]

    def generate(self, output_folder: Path):
        StopListGeneratorComponent(self.stop_data).generate(output_folder)
        RouteListGeneratorComponent(self.route_data).generate(output_folder)
        StopTimesGeneratorComponent(self.stop_time_data, self.trip_data).generate(output_folder)
