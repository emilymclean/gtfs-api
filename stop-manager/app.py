import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import pandas as pd
import yaml

from flask import Flask, render_template, jsonify, request


@dataclass
class StopGrouping:
    stop_id: str
    name: str
    children: List[str]


app = Flask(__name__)


def load_yaml() -> List[StopGrouping]:
    groups = yaml.safe_load(Path(os.environ["GROUPS_CONFIG_FILE"]).read_text())
    if groups is None or "groupings" not in groups:
        return []
    groupings = groups["groupings"]

    out = []
    for grouping in groupings:
        out.append(StopGrouping(
            stop_id=grouping["stop_id"],
            name=grouping["name"],
            children=grouping["children"],
        ))

    return out


def parent_station(stop_id: str, groupings: List[StopGrouping]) -> Optional[str]:
    for grouping in groupings:
        for child in grouping.children:
            if child == stop_id:
                return grouping.stop_id
    return None

@app.route('/')
def index():
    return render_template('index.html')


@app.get('/stops/list')
def stop_list():
    groupings = load_yaml()
    stops_list_paths = os.environ["STOPS_LIST_LOCATION"].split(",")
    stops = []
    for stop_list_path in stops_list_paths:
        df = pd.read_csv(Path(stop_list_path), keep_default_na=False)

        for i, stop in df.iterrows():
            if "parent_station" in stop and stop["parent_station"] != "":
                parent = stop["parent_station"]
            else:
                parent = parent_station(stop["stop_id"], groupings)

            stops.append({
                "id": stop["stop_id"],
                "name": stop["stop_name"],
                "lat": stop["stop_lat"],
                "lng": stop["stop_lon"],
                "parent_station_id": parent,
            })
    return stops


@app.post("/group/create")
def group_create():
    json = request.json
    existing = load_yaml()
    existing.append(StopGrouping(
        json["stop_id"],
        json["name"],
        json["children"]
    ))

    Path(os.environ["GROUPS_CONFIG_FILE"]).write_text(
        yaml.dump({
            "groupings": [asdict(x) for x in existing]
        })
    )
    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True)