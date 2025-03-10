from dataclasses import dataclass
from typing import Optional, List, TypeVar, Generic

import pandas as pd

stops_endpoint = "stops.json"
routes_endpoint = "routes.json"

T = TypeVar("T")

@dataclass
class GtfsCsv:
    data: pd.DataFrame
    distinguisher: Optional[str]


@dataclass
class ParsedCsv(Generic[T]):
    data: T
    distinguisher: Optional[str]


def filter_parsed_by_distinguisher(parsed: List[ParsedCsv[T]], distinguisher: Optional[str]) -> List[ParsedCsv[T]]:
    return filter(lambda x: x.distinguisher == distinguisher, parsed) if distinguisher is not None else parsed


def flatten_parsed(parsed: List[ParsedCsv[List[T]]]) -> List[T]:
    return [x for xs in parsed for x in xs.data]


def filter_and_combine_gtfs(gtfs: List[GtfsCsv], distinguisher: Optional[str]) -> pd.DataFrame:
    filtered = filter(lambda x: x.distinguisher == distinguisher, gtfs) if distinguisher is not None else gtfs
    return pd.concat([x.data for x in filtered])
