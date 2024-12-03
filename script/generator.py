import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import List, Optional, Any, AnyStr, TypeVar, Generic

from google.protobuf.message import Message

import format_pb2 as pb

import pandas as pd

from consts import *

stops_endpoint = "stops.json"
routes_endpoint = "routes.json"


@dataclass
class GtfsCsv:
    data: pd.DataFrame
    distinguisher: Optional[str]


class Generator:

    def __init__(
            self,
            stop_csvs: List[GtfsCsv],
            route_csvs: List[GtfsCsv],
    ):
        self.stop_csvs = stop_csvs
        self.route_csvs = route_csvs

        stop = pb.Stop()
        stop.id = "test"
        print(stop)

    def generate(self, output_folder: Path):
        StopListGenerator(self.stop_csvs, output_folder).generate()
        RouteListGenerator(self.route_csvs, output_folder).generate()


class GeneratorComponent(ABC):
    _output_folder: Path

    def __init__(self, output_folder: Path):
        self._output_folder = output_folder

    @abstractmethod
    def generate(self):
        pass

    def _write_distinguished(self, data: AnyStr, distinguisher: Optional[str], path: str | PathLike):
        if distinguisher is None:
            return

        self._write(data, Path(distinguisher).joinpath(path))

    @abstractmethod
    def _write(self, data: AnyStr, path: str | PathLike):
        path = self._output_folder.joinpath(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            f.write(data)








class StopListGenerator(ListGeneratorComponent):

    def __init__(self, stops_csvs: List[GtfsCsv], output_folder: Path):
        super().__init__(output_folder)
        self.csvs = stops_csvs
        self.endpoint = stops_endpoint

    def _generate_single_json(self, csv: GtfsCsv) -> List:
        stops = []
        for index, entry in csv.data.iterrows():
            stops.append(
                {
                    "id": entry['stop_id'],
                    "name": entry['stop_name'],
                    "location": {
                        "lat": entry['stop_lat'],
                        "lng": entry['stop_lon'],
                    },
                    "accessibility": {
                        "wheelchair": wheelchair_boarding_options[entry['wheelchair_boarding']],
                    }
                }
            )
        return stops

    def _generate_single_pb(self, csv: GtfsCsv) -> List[Message]:
        stops = []
        for index, entry in csv.data.iterrows():
            stop = pb.Stop()
            stop.id = entry['stop_id']
            stop.name = entry['stop_name']

            location = pb.Location()
            location.lat = entry['stop_lat']
            location.lng = entry['stop_lat']
            stop.location = location

            accessibility = pb.StopAccessibility()
            accessibility.wheelchair = wheelchair_boarding_options_pb[entry['wheelchair_boarding']]
            stop.accessibility = accessibility
            stops.append(stop)
        return stops


class RouteListGenerator(ListGeneratorComponent):
    def __init__(self, route_csvs: List[GtfsCsv], output_folder: Path):
        super().__init__(output_folder)
        self.csvs = route_csvs
        self.endpoint = routes_endpoint

    def _generate_single_json(self, csv: GtfsCsv) -> List:
        routes = []
        for index, entry in csv.data.iterrows():
            routes.append(
                {
                    "id": entry['route_id'],
                    "code": f"{entry['route_short_name']}",
                    "name": entry['route_long_name'],
                    "type": route_type_options[entry['route_type']],
                }
            )
        return routes