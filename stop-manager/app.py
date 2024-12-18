import os
from pathlib import Path

import pandas as pd

from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.get('/stops/list')
def stop_list():
    stops_list_paths = os.environ["STOPS_LIST_LOCATION"].split(",")
    stops = []
    print(stops_list_paths)
    for stop_list_path in stops_list_paths:
        df = pd.read_csv(Path(stop_list_path), keep_default_na=False)
        for i, stop in df.iterrows():
            stops.append({
                "id": stop["stop_id"],
                "name": stop["stop_name"],
                "lat": stop["stop_lat"],
                "lng": stop["stop_lon"],
            })
    return stops

if __name__ == "__main__":
    app.run(debug=True)