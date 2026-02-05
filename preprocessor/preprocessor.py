import base64
import hashlib
from pathlib import Path

import click
import pandas as pd


def map_route_id(route_id: str) -> str:
    r = route_id.partition("_")[0]

    if r == "1":
        return "ACTO001"
    elif r == "X1" or r == "X2":
        return r
    else:
        return f"{r}-10657"


def map_route_name(route_name: str) -> str:
    return route_name.removeprefix("S - ")


def route_is_school_only(route_id: str) -> bool:
    try:
        return int(route_id.partition("_")[0]) >= 1000
    except ValueError:
        return False


def combine_routes(df: pd.DataFrame):
    return df.drop_duplicates(subset='route_id', keep='first')


service_id_map = {}


def generate_service_id_map(calendar_csv: pd.DataFrame):
    for index, row in calendar_csv.iterrows():
        service_id_map[f"{row['service_id']}"] = (f"{row['service_id']}-" +
            base64.urlsafe_b64encode(
                hashlib.sha1((f"{row['monday']},{row['tuesday']},"
                              f"{row['wednesday']},{row['thursday']},{row['friday']},"
                              f"{row['saturday']},{row['sunday']},{row['start_date']},"
                              f"{row['end_date']}").encode("utf-8")).digest()
            ).decode("utf-8")[0:16])


def map_service_id(service_id: str) -> str:
    return service_id_map[f"{service_id}"]


def stop_is_school_only(stop_name: str) -> bool:
    return stop_name.endswith(" SSO")


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

    route_csv['school'] = route_csv['route_id'].apply(route_is_school_only)
    stop_csv['school'] = stop_csv['stop_name'].apply(stop_is_school_only)

    generate_service_id_map(calendar_csv)

    calendar_csv['service_id'] = calendar_csv['service_id'].apply(map_service_id)
    calendar_date_csv['service_id'] = calendar_date_csv['service_id'].apply(map_service_id)
    trips_csv['service_id'] = trips_csv['service_id'].apply(map_service_id)

    route_csv['route_id'] = route_csv['route_id'].apply(map_route_id)
    trips_csv['route_id'] = trips_csv['route_id'].apply(map_route_id)

    route_csv['route_long_name'] = route_csv['route_long_name'].apply(map_route_name)

    route_csv = combine_routes(route_csv)

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
