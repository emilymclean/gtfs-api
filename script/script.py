from pathlib import Path
from typing import List, TypeVar, Optional

import click
import pandas as pd
import yaml

from gen.generator import Generator
from gen.models import GtfsCsv

T = TypeVar("T")


def get_if_in_bounds(l: List[T], index: int) -> Optional[T]:
    if len(l) > index:
        return l[index]
    return None


def read_csv(path: str, folders: List[str], distinguisher: List[str]) -> list[GtfsCsv]:
    return [GtfsCsv(
        pd.read_csv(Path(f).joinpath(path), keep_default_na=False),
        get_if_in_bounds(distinguisher, i)
    ) for i, f in enumerate(folders)]


@click.command
@click.option('--input-folder', '-i', multiple=True, required=True)
@click.option('--distinguisher', '-d', multiple=True, required=False)
@click.option('--config', '-c', required=True)
@click.option('--output-folder', '-o')
def generate(input_folder: List[str], distinguisher: List[str], config: str, output_folder: str):
    stop_csvs = read_csv("stops.txt", input_folder, distinguisher)
    route_csvs = read_csv("routes.txt", input_folder, distinguisher)
    calendar_csvs = read_csv("calendar.txt", input_folder, distinguisher)
    calendar_date_csvs = read_csv("calendar_dates.txt", input_folder, distinguisher)
    shape_csvs = read_csv("shapes.txt", input_folder, distinguisher)
    stop_time_csvs = read_csv("stop_times.txt", input_folder, distinguisher)
    trips_csvs = read_csv("trips.txt", input_folder, distinguisher)
    with Path(config).open('r') as f:
        config = yaml.safe_load(f.read())

    Generator(
        stop_csvs,
        route_csvs,
        calendar_csvs,
        calendar_date_csvs,
        shape_csvs,
        stop_time_csvs,
        trips_csvs,
        config
    ).generate(Path(output_folder))


if __name__ == '__main__':
    generate()