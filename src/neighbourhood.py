import polars as pl
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class ReportingNeighbourhoods:
    reporting_unit_to_neighbourhood: Dict[str, Optional[str]]
    neighbourhood_to_reporting_units: Dict[str, List[str]]


class NeighbourhoodData:
    data: pl.LazyFrame

    def __init__(self, data) -> None:
        self.data = data

    @staticmethod
    def from_path(str_path: Optional[str]):
        if str_path == None:
            return None

        try:
            path = Path(str_path)
            data = None
            if path.suffix == ".csv":
                data = pl.scan_csv(path)
            elif path.suffix == ".parquet":
                data = pl.scan_parquet(path)
            else:
                return None
        except Exception:
            return None

        if data.columns != ["zip_code", "neighbourhood_code", "ambiguous"]:
            return None

        return NeighbourhoodData(data=data)
