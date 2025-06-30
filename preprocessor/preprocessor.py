from pathlib import Path

import click
import pandas as pd


def map_route(route_id: str) -> str:
    r = route_id.partition("_")[0]

    if r == "1":
        return "ACTO001"
    elif r == "X1" or r == "X2":
        return r
    else:
        return f"{r}-10657"


def combine_routes(df: pd.DataFrame):
    return df.drop_duplicates(subset='route_id', keep='first')


@click.group()
def cli() -> None:
    pass


@click.command()
@click.option('--input-folder', '-i', required=True)
@click.option('--output-folder', '-o', required=True)
def process(
    input_folder: str,
    output_folder: str,
):
    stop_csv = pd.read_csv(Path(input_folder).joinpath("stops.txt"), keep_default_na=False)
    route_csv = pd.read_csv(Path(input_folder).joinpath("routes.txt"), keep_default_na=False)
    calendar_csv = pd.read_csv(Path(input_folder).joinpath("calendar.txt"), keep_default_na=False)
    calendar_date_csv = pd.read_csv(Path(input_folder).joinpath("calendar_dates.txt"), keep_default_na=False)
    shape_csv = pd.read_csv(Path(input_folder).joinpath("shapes.txt"), keep_default_na=False)
    stop_time_csv = pd.read_csv(Path(input_folder).joinpath("stop_times.txt"), keep_default_na=False)
    trips_csv = pd.read_csv(Path(input_folder).joinpath("trips.txt"), keep_default_na=False)

    route_csv['route_id'] = route_csv['route_id'].apply(map_route)
    route_csv = combine_routes(route_csv)

    trips_csv['route_id'] = trips_csv['route_id'].apply(map_route)

    Path(output_folder).mkdir(parents=True, exist_ok=True)
    stop_csv.to_csv(Path(output_folder).joinpath("stops.txt"), index=False)
    route_csv.to_csv(Path(output_folder).joinpath("routes.txt"), index=False)
    calendar_csv.to_csv(Path(output_folder).joinpath("calendar.txt"), index=False)
    calendar_date_csv.to_csv(Path(output_folder).joinpath("calendar_dates.txt"), index=False)
    shape_csv.to_csv(Path(output_folder).joinpath("shapes.txt"), index=False)
    stop_time_csv.to_csv(Path(output_folder).joinpath("stop_times.txt"), index=False)
    trips_csv.to_csv(Path(output_folder).joinpath("trips.txt"), index=False)


if __name__ == '__main__':
    cli.add_command(process)
    cli()
