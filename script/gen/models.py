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