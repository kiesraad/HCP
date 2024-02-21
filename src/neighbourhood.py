import polars as pl
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ReportingNeighbourhoods:
    reporting_unit_to_neighbourhood: Dict[str, Optional[str]]
    neighbourhood_to_reporting_units: Dict[str, List[str]]

    def get_reference_group(self, reporting_unit_id: str) -> List[str]:
        neighbourhood = self.reporting_unit_to_neighbourhood.get(reporting_unit_id)
        if not neighbourhood:
            return []
        else:
            return [
                comparison_id
                for comparison_id in self.neighbourhood_to_reporting_units[
                    neighbourhood
                ]
                if comparison_id != reporting_unit_id
            ]


class NeighbourhoodData:
    data: pl.LazyFrame

    def __init__(self, data) -> None:
        self.data = data

    def fetch_neighbourhood_code(self, zip_code: str) -> str:
        queried_result = (
            self.data.filter(pl.col("zip_code") == zip_code)
            .select("neighbourhood_code")
            .collect()
        )
        return queried_result.item()

    def fetch_reporting_neighbourhoods(
        self, reporting_unit_zips: Dict[str, Optional[str]]
    ) -> ReportingNeighbourhoods:
        zips = set((zip for zip in reporting_unit_zips.values() if zip is not None))
        zips_to_neighbourhoods = {
            zip: self.fetch_neighbourhood_code(zip) for zip in zips
        }

        reporting_unit_to_neighbourhood = {}
        for reporting_unit_id, zip in reporting_unit_zips.items():
            if zip is None:
                reporting_unit_to_neighbourhood[reporting_unit_id] = None
            else:
                reporting_unit_to_neighbourhood[reporting_unit_id] = (
                    zips_to_neighbourhoods[zip]
                )

        neighbourhood_to_reporting_units = defaultdict(list)
        for (
            reporting_unit_id,
            neighbourhood_code,
        ) in reporting_unit_to_neighbourhood.items():
            if neighbourhood_code:
                neighbourhood_to_reporting_units[neighbourhood_code].append(
                    reporting_unit_id
                )

        return ReportingNeighbourhoods(
            reporting_unit_to_neighbourhood=reporting_unit_to_neighbourhood,
            neighbourhood_to_reporting_units=neighbourhood_to_reporting_units,
        )

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
