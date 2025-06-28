from pathlib import Path
from typing import Dict, Callable, Any

from .component import GeneratorComponent
from .component.extras_helper import _get_name_stop
from .component.intermediaries import StopCSV, RouteCSV, CalendarCSV, CalendarExceptionCSV, StopTimeCSV, TripCSV, \
    StopAccessibilityCSV
from .component.route_canonical_timetable_generator import RouteCanonicalTimetableGeneratorComponent
from .component.route_detail_generator import RouteDetailGeneratorComponent
from .component.route_headings_generator import RouteHeadingsGeneratorComponent
from .component.route_list_generator import RouteListGeneratorComponent
from .component.route_service_generator import RouteServiceGeneratorComponent
from .component.route_timetable_generator import RouteTimetableGeneratorComponent
from .component.service_list_generator import ServiceListGeneratorComponent
from .component.stop_detail_generator import StopDetailGeneratorComponent
from .component.stop_list_generator import StopListGeneratorComponent
from .component.stop_routes_generator import StopRoutesGeneratorComponent
from .component.stop_timetable_generator import StopTimetableGeneratorComponent
from .component.trip_index_generator import TripIndexGeneratorComponent
from .component.trip_timetable_generator import TripTimetableGeneratorComponent
from .component.v2.route_canonical_timetable_generator_v2 import RouteCanonicalTimetableGeneratorV2Component
from .location_helper import LocationHelper
from .models import *
from .raptor.byte_graph_generator import ByteNetworkGraphGenerator
from .time_helper import TimeHelper

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
            config: Dict[str, Any],
            groups: Optional[Dict[str, Any]]
    ):
        self.config = config
        self.groups = groups
        self.time_helper = TimeHelper(config.get("timezone", "UTC"))

        print("Parsing data")
        self.stop_data = [ParsedCsv[List[StopCSV]](StopCSV.from_csv(p.data), p.distinguisher) for p in stop_csvs]
        self.route_data = [ParsedCsv[List[RouteCSV]](RouteCSV.from_csv(p.data), p.distinguisher) for p in route_csvs]
        self.calendar_data = [ParsedCsv[List[CalendarCSV]](CalendarCSV.from_csv(p.data, self.time_helper), p.distinguisher) for p in calendar_csvs]
        self.calendar_exception_data = [ParsedCsv[List[CalendarExceptionCSV]](CalendarExceptionCSV.from_csv(p.data, self.time_helper), p.distinguisher) for p in calendar_date_csvs]
        self.stop_time_data = [ParsedCsv[List[StopTimeCSV]](StopTimeCSV.from_csv(p.data, self.time_helper), p.distinguisher) for p in stop_time_csvs]
        self.trip_data = [ParsedCsv[List[TripCSV]](TripCSV.from_csv(p.data), p.distinguisher) for p in trip_csvs]

        # self._index(route_csvs)
        self._modify()
        self._index(route_csvs)

    def _modify(self):
        print("Modifying data")

        # Rename stops
        # This should really generically apply all stops
        for p in self.stop_data:
            for s in p.data:
                s: StopCSV = s
                rename = _get_name_stop(s.id, self.config)
                if rename is None:
                    continue
                s.name = rename

        # Setup groups
        self._add_groupings()

    def _add_groupings(self):
        self.stop_index = self._create_index(flatten_parsed(self.stop_data), lambda x: x.id)
        self.stop_index_by_parent = {}

        groupings: List[Dict[str, Any]] | None = self.groups.get("groupings", None) if self.groups is not None else None

        if groupings is None:
            return

        added_stops = []

        for g in groupings:
            name: str | None = g.get("name", None)
            stop_id: str | None = g.get("stop_id", None)
            children: List[str] | None = g.get("children", [])

            if name is None or stop_id is None or len(children) == 0:
                continue
            
            children_stop = [self.stop_index[f"{s}"] for s in children if f"{s}" in self.stop_index]
            if len(children_stop) == 0:
                continue
            midpoint = LocationHelper.midpoint([s.location for s in children_stop])
            wheelchair_accessibility = min([s.accessibility.wheelchair for s in children_stop])

            for child in children_stop:
                all_stops: List[List[StopCSV]] = ([d.data for d in self.stop_data] + [added_stops])
                for p in all_stops:
                    child_stop = next(filter(lambda x: x.id == child.id, p), None)
                    if child_stop is None:
                        continue
                    child_stop.parent_station = stop_id

            stop = StopCSV(
                stop_id,
                name,
                None,
                midpoint,
                StopAccessibilityCSV(
                    wheelchair_accessibility
                )
            )

            added_stops.append(stop)

            self.stop_index[stop_id] = stop
            self.stop_index_by_parent = self.stop_index_by_parent | self._create_list_index(children_stop,
                                                                                            lambda s: stop_id)

        self.stop_data.append(ParsedCsv(added_stops, "added"))

    def _index(self, route_csvs: List[GtfsCsv]):
        print("Generating indexes")
        self.stop_index = self.stop_index | self._create_index(flatten_parsed(self.stop_data), lambda x: x.id)
        self.stop_index_by_parent = self.stop_index_by_parent | self._create_list_index(
            filter(lambda x: x.parent_station is not None, flatten_parsed(self.stop_data)), lambda x: x.parent_station)
        self.stop_time_index = self._create_list_index(flatten_parsed(self.stop_time_data), lambda x: x.stop_id)
        self.stop_time_index_by_trip = self._create_list_index(flatten_parsed(self.stop_time_data), lambda x: x.trip_id)
        self.route_index = self._create_index(flatten_parsed(self.route_data), lambda x: x.id)
        self.trip_index = self._create_index(flatten_parsed(self.trip_data), lambda x: x.id)
        self.trip_index_by_service = self._create_list_index(flatten_parsed(self.trip_data), lambda x: x.service_id)
        self.trip_index_by_route = self._create_list_index(flatten_parsed(self.trip_data), lambda x: x.route_id)
        self.calendar_index = self._create_list_index(flatten_parsed(self.calendar_data), lambda x: x.service_id)
        self.calendar_exception_index = self._create_list_index(flatten_parsed(self.calendar_exception_data),
                                                                lambda x: x.service_id)

        self.distinguishers = list(filter(lambda x: x is not None, [d.distinguisher for d in route_csvs]))
        print("Finished setup")

    def generate(self, output_folder: Path):
        generators = [
            StopListGeneratorComponent(self.stop_data, self.distinguishers),
            StopDetailGeneratorComponent(self.stop_data, self.stop_index_by_parent, self.distinguishers),
            StopRoutesGeneratorComponent(self.stop_time_data, self.trip_index, self.distinguishers),
            RouteListGeneratorComponent(self.route_data, self.distinguishers),
            RouteDetailGeneratorComponent(self.route_data, self.distinguishers),
            RouteTimetableGeneratorComponent(
                self.route_data,
                self.trip_index_by_route,
                self.stop_time_index_by_trip,
                self.distinguishers
            ),
            RouteCanonicalTimetableGeneratorComponent(
                self.route_data,
                self.trip_index_by_route,
                self.stop_time_index_by_trip,
                self.stop_index,
                self.distinguishers
            ),
            RouteCanonicalTimetableGeneratorV2Component(
                self.route_data,
                self.trip_index_by_route,
                self.stop_time_index_by_trip,
                self.stop_index,
                self.distinguishers
            ),
            TripTimetableGeneratorComponent(
                self.route_data,
                self.trip_index_by_route,
                self.stop_time_index_by_trip,
                self.distinguishers
            ),
            RouteServiceGeneratorComponent(
                self.route_data,
                self.trip_index_by_route,
                self.distinguishers
            ),
            RouteHeadingsGeneratorComponent(
                self.route_data,
                self.trip_index_by_route,
                self.distinguishers
            ),
            StopTimetableGeneratorComponent(
                self.stop_data,
                self.stop_time_index,
                self.stop_index_by_parent,
                self.trip_index,
                self.route_index,
                self.calendar_index,
                self.calendar_exception_index,
                self.distinguishers
            ),
            ServiceListGeneratorComponent(self.calendar_data, self.calendar_exception_index, self.trip_index_by_service, self.distinguishers)
        ]

        self._do_generation(generators, output_folder)

    def network_graph(self, output_folder: Path):
        g = ByteNetworkGraphGenerator(
            flatten_parsed(self.stop_data),
            self.route_index,
            flatten_parsed(self.trip_data),
            self.stop_time_index_by_trip
        )
        g.time_helper = self.time_helper
        g.generate(output_folder)

    def generate_trip_index(self, output_folder: Path):
        generators = [
            TripIndexGeneratorComponent(
                self.trip_data,
                self.route_index,
                self.stop_time_index_by_trip,
                self.stop_index,
                self.distinguishers
            )
        ]

        self._do_generation(generators, output_folder)

    def _do_generation(self, generators: List[GeneratorComponent], output_folder: Path):
        for g in generators:
            g.config = self.config
            g.time_helper = self.time_helper
            g.generate(output_folder)

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