import polars as pl
from pathlib import Path
from typing import Optional, List, Dict, TypeVar, Set
from dataclasses import dataclass
from collections import defaultdict
from eml_types import ReportingUnitInfo

T = TypeVar("T")


def _add_dict(a: Dict[T, int], b: Dict[T, int]) -> Dict[T, int]:
    return {key_a: a[key_a] + b[key_a] for key_a in a.keys()}


@dataclass
class ReportingNeighbourhoods:
    reporting_unit_id_to_neighbourhood_id: Dict[str, Optional[str]]
    neighbourhood_id_to_reporting_unit_ids: Dict[str, Set[str]]
    neighbourhood_id_to_reference_group: Dict[str, ReportingUnitInfo]


class NeighbourhoodData:
    data: pl.LazyFrame

    def __init__(self, data) -> None:
        self.data = data

    def fetch_neighbourhood_code(self, zip_code: str) -> Optional[str]:
        queried_result = (
            self.data.filter(pl.col("zip_code") == zip_code)
            .select("neighbourhood_code")
            .collect()
        )
        if len(queried_result) != 1:
            return None
        return queried_result.item()

    def fetch_reporting_neighbourhoods(
        self,
        reporting_unit_zips: Dict[str, Optional[str]],
        reporting_unit_info: Dict[str, ReportingUnitInfo],
    ) -> ReportingNeighbourhoods:
        # Fetch the neighbourhood codes for all unique zips
        zips = set((zip for zip in reporting_unit_zips.values() if zip is not None))
        zips_to_neighbourhoods = {
            zip: self.fetch_neighbourhood_code(zip) for zip in zips
        }

        # Construct mapping from reporting unit id to neighbourhood id
        reporting_unit_id_to_neighbourhood_id = {}
        for reporting_unit_id, zip in reporting_unit_zips.items():
            if zip is None:
                reporting_unit_id_to_neighbourhood_id[reporting_unit_id] = None
            else:
                reporting_unit_id_to_neighbourhood_id[reporting_unit_id] = (
                    zips_to_neighbourhoods[zip]
                )

        # Construct mapping from neighbourhood id to reporting unit id list
        neighbourhood_id_to_reporting_unit_ids = defaultdict(set)
        for (
            reporting_unit_id,
            neighbourhood_code,
        ) in reporting_unit_id_to_neighbourhood_id.items():
            if neighbourhood_code:
                neighbourhood_id_to_reporting_unit_ids[neighbourhood_code].add(
                    reporting_unit_id
                )

        # Given the mapping from neighbourhood ids to reporting unit ids, constuct reporting unit objects
        neighbourhood_id_to_reference_group = {}
        for (
            neighbourhood_id,
            reporting_unit_ids,
        ) in neighbourhood_id_to_reporting_unit_ids.items():

            # Construct the reference group vote counts by adding dicts of the reporting ids
            # that belong to this neighbourhood
            summed_votes_per_party = {}
            summed_votes_per_candidate = {}
            for reporting_unit_id, reporting_unit in reporting_unit_info.items():
                if reporting_unit_id not in reporting_unit_ids:
                    continue

                if len(summed_votes_per_party) == 0:
                    summed_votes_per_party = reporting_unit.votes_per_party
                else:
                    summed_votes_per_party = _add_dict(
                        summed_votes_per_party, reporting_unit.votes_per_party
                    )

                if len(summed_votes_per_candidate) == 0:
                    summed_votes_per_candidate = reporting_unit.votes_per_candidate
                else:
                    summed_votes_per_candidate = _add_dict(
                        summed_votes_per_candidate, reporting_unit.votes_per_candidate
                    )

            neighbourhood_id_to_reference_group[neighbourhood_id] = ReportingUnitInfo(
                reporting_unit_id=neighbourhood_id,
                reporting_unit_name=f"Reference group for {neighbourhood_id}",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party=summed_votes_per_party,
                votes_per_candidate=summed_votes_per_candidate,
            )

        return ReportingNeighbourhoods(
            reporting_unit_id_to_neighbourhood_id=reporting_unit_id_to_neighbourhood_id,
            neighbourhood_id_to_reporting_unit_ids=neighbourhood_id_to_reporting_unit_ids,
            neighbourhood_id_to_reference_group=neighbourhood_id_to_reference_group,
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
