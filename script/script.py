from pathlib import Path
from typing import List, TypeVar, Optional

import click
import pandas as pd

from gen.generator import Generator
from gen.models import GtfsCsv

T = TypeVar("T")


def get_if_in_bounds(l: List[T], index: int) -> Optional[T]:
    if len(l) > index:
        return l[index]
    return None


def read_csv(path: str, folders: List[str], distinguisher: List[str]) -> list[GtfsCsv]:
    return [GtfsCsv(
        pd.read_csv(Path(f).joinpath(path)),
        get_if_in_bounds(distinguisher, i)
    ) for i, f in enumerate(folders)]


@click.command
@click.option('--input-folder', '-i', multiple=True, required=True)
@click.option('--distinguisher', '-d', multiple=True, required=False)
@click.option('--output-folder', '-o')
def generate(input_folder: List[str], distinguisher: List[str], output_folder: str):
    stop_csvs = read_csv("stops.txt", input_folder, distinguisher)
    route_csvs = read_csv("routes.txt", input_folder, distinguisher)
    Generator(stop_csvs, route_csvs).generate(Path(output_folder))


if __name__ == '__main__':
    generate()