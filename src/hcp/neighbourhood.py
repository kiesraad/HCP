import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set, TypeVar

import polars as pl

from .eml_types import ReportingUnitInfo

T = TypeVar("T")
REGEX_NON_NEIGHBOURHOOD_NAME = re.compile(
    r"brief|station|mobiel|metro|cabin|tent|tijdelijk", flags=re.IGNORECASE
)


def _name_is_non_neighbourhood(name: Optional[str]) -> bool:
    if name is None:
        return False
    return bool(re.search(REGEX_NON_NEIGHBOURHOOD_NAME, name))


def _add_dict(a: Dict[T, int], b: Dict[T, int]) -> Dict[T, int]:
    return {key_a: a[key_a] + b[key_a] for key_a in a.keys()}


@dataclass
class ReportingNeighbourhoods:
    """Container which contains several mappings used for running checks at
    a neighbourhood level. The combination of these mappings can then be used
    to look up a reference `ReportingUnitInfo` for a given reporting unit id
    by hopping from `reportinging_unit_id` -> `neighbourhood_id` ->
    `ReportingUnitInfo`.

    This 'reference_group' is a `ReportingUnitInfo` instance which is the sum
    of all reporting unit vote counts which are in the same
    neighbourhood as the specified reporting unit.

    The following mappings are present:
        - reporting_unit_id_to_neighbourhood_id: used for lookup of neighbourhood
        corresponding to specified reporting unit id.
        - neighbourhood_id_to_reporting_unit_ids: used for getting all reporting
        unit ids which are in the given neighbourhood.
        - neighbourhood_id_to_reference_group: used for lookup of reference group
        for a given neighbourhood id.

    """

    reporting_unit_id_to_neighbourhood_id: Dict[str, Optional[str]]
    neighbourhood_id_to_reporting_unit_ids: Dict[str, Set[str]]
    neighbourhood_id_to_reference_group: Dict[str, ReportingUnitInfo]

    def get_reference_group(
        self, reporting_unit_id: str
    ) -> Optional[ReportingUnitInfo]:
        """Get the reference group for a given reporting unit id.

        Args:
            reporting_unit_id: The reporting unit id to query for.

        Returns:
            An optional `ReportingUnitInfo` instance which contains the sum of all vote counts
            of all reporting units in that neighbourhood.
        """
        neighbourhood_id = self.reporting_unit_id_to_neighbourhood_id[reporting_unit_id]
        if not neighbourhood_id:
            return None
        return self.neighbourhood_id_to_reference_group[neighbourhood_id]

    def get_reference_size(self, reporting_unit_id: str) -> int:
        """Get the reference size (amount of reporting units) in the associated neighbourhood
        for a given `reporting_unit_id`. Note that the reporting unit itself is also included
        in this size.

        Args:
            reporting_unit_id: The reporting unit id to query for

        Returns:
            The amount of reporting units present in the corresponding neighbourhood.

        """
        neighbourhood_id = self.reporting_unit_id_to_neighbourhood_id[reporting_unit_id]
        if not neighbourhood_id:
            return 0
        return len(self.neighbourhood_id_to_reporting_unit_ids[neighbourhood_id])


@dataclass
class NeighbourhoodData:
    """Class containing a **lazy** dataframe containing neighbourhood data.
    This allows you to call the defined methods on this lazyframe, without
    having to load in all the neighbourhood data to memory.
    """

    data: pl.LazyFrame

    def fetch_neighbourhood_code(self, zip_code: str) -> Optional[str]:
        """Given a specified zip_code, return the corresponding neighbourhood
        code as specified in the neighbourhood data.

        Args:
            zip_code: Zip code to query the data for, without spaces (e.g. `1011AB`)

        Returns:
            The corresponding neighbourhood code (e.g. `WK0363AF`) if the zip code was found
        """
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
        """Constructs a `ReportingNeighbourhoods` instance for the given
        neighbourhood data. The reference groups are calculated by summing
        up the votes per party and the votes per candidate for all reporting
        units and constructing a new `ReportingUnitInfo` instance for each
        neighbourhood.

        Args:
            reporting_unit_zips: Mapping from reporting unit id to the associated zip code.
            reporting_unit_info: Mapping from reporting unit id to the `ReportingUnitInfo`.

        Returns:
            Instance of `ReportingNeighbourhoods`.
        """
        # Fetch the neighbourhood codes for all unique zips
        zips = set((zip for zip in reporting_unit_zips.values() if zip is not None))
        zips_to_neighbourhoods = {
            zip: self.fetch_neighbourhood_code(zip) for zip in zips
        }

        # Construct mapping from reporting unit id to neighbourhood id
        reporting_unit_id_to_neighbourhood_id = {}
        for reporting_unit_id, zip in reporting_unit_zips.items():
            if zip is None or _name_is_non_neighbourhood(
                reporting_unit_info[reporting_unit_id].reporting_unit_name
            ):
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
    def from_path(str_path: Optional[str]) -> Optional["NeighbourhoodData"]:
        """Construct an instance of `NeihbourhoodData` from a given path.

        Returns:
            `NeighbourhoodData` instance if path was specified, `None` otherwise.
        """
        if str_path is None:
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
