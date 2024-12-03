from pathlib import Path
from typing import List

from .component.stop_list_generator import StopListGeneratorComponent
from .component.intermediaries import StopCSV, RouteCSV
from .component.route_list_generator import RouteListGeneratorComponent
from .models import *


class Generator:

    def __init__(
            self,
            stop_csvs: List[GtfsCsv],
            route_csvs: List[GtfsCsv],
    ):
        self.stop_data = [ParsedCsv[List[StopCSV]](StopCSV.from_csv(p.data), p.distinguisher) for p in stop_csvs]
        self.route_data = [ParsedCsv[List[RouteCSV]](RouteCSV.from_csv(p.data), p.distinguisher) for p in route_csvs]

    def generate(self, output_folder: Path):
        StopListGeneratorComponent(self.stop_data).generate(output_folder)
        RouteListGeneratorComponent(self.route_data).generate(output_folder)
