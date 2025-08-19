from itertools import repeat
from typing import Dict, Optional

import pytest

from hcp.eml_types import CandidateIdentifier, PartyIdentifier, ReportingUnitInfo
from hcp.neighbourhood import NeighbourhoodData, ReportingNeighbourhoods

read_test_cases = [
    ("./test/data/neighbourhood_files/valid.parquet", True),
    ("./test/data/neighbourhood_files/valid.csv", True),
    ("./test/data/neighbourhood_files/THIS_FILE_DOES_NOT_EXIST.parquet", False),
    ("./test/data/THIS_FOLDER_DOES_NOT_EXIST/valid.parquet", False),
    ("./test/data/neighbourhood_files/wrong_filetype.txt", False),
    ("./test/data/neighbourhood_files/invalid.csv", False),
    (None, False),
]


@pytest.mark.parametrize("path_to_read, should_load", read_test_cases)
def test_read_neighbourhood_file(
    path_to_read: Optional[str], should_load: bool
) -> None:
    result = NeighbourhoodData.from_path(path_to_read)
    if should_load:
        assert isinstance(result, NeighbourhoodData)
    else:
        assert result is None


fetch_test_cases = [
    ("./test/data/neighbourhood_files/valid.csv", "1234AB", "WK123"),
    ("./test/data/neighbourhood_files/valid.csv", "1235AB", "WK123"),
    ("./test/data/neighbourhood_files/valid.csv", "1234AC", None),
]


@pytest.mark.parametrize("path_to_read, zip_code, expected", fetch_test_cases)
def test_fetch_neighbourhood_code(
    path_to_read: str, zip_code: str, expected: Optional[str]
) -> None:
    data = NeighbourhoodData.from_path(path_to_read)
    assert data is not None and data.fetch_neighbourhood_code(zip_code) == expected


reporting_neighbourhoods_test_cases = [
    (
        "./test/data/neighbourhood_files/valid.csv",
        {"SB1": "1234AB", "SB2": "1235AB", "SB3": "9999XX", "SB4": None},
        {
            "SB1": ReportingUnitInfo(
                reporting_unit_id="SB1",
                reporting_unit_name="SB1",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 10},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 8,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 2,
                },
            ),
            "SB2": ReportingUnitInfo(
                reporting_unit_id="SB2",
                reporting_unit_name="SB2",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 12},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 11,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 1,
                },
            ),
            "SB3": ReportingUnitInfo(
                reporting_unit_id="SB3",
                reporting_unit_name="SB3",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 100},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 80,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 20,
                },
            ),
            "SB4": ReportingUnitInfo(
                reporting_unit_id="SB4",
                reporting_unit_name="SB4",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 200},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 160,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 40,
                },
            ),
        },
        ReportingNeighbourhoods(
            reporting_unit_id_to_neighbourhood_id={
                "SB1": "WK123",
                "SB2": "WK123",
                "SB3": None,
                "SB4": None,
            },
            neighbourhood_id_to_reporting_unit_ids={"WK123": set(["SB1", "SB2"])},
            neighbourhood_id_to_reference_group={
                "WK123": ReportingUnitInfo(
                    reporting_unit_id="WK123",
                    reporting_unit_name="Reference group for WK123",
                    cast=0,
                    total_counted=0,
                    rejected_votes={},
                    uncounted_votes={},
                    votes_per_party={PartyIdentifier(id=1, name=None): 22},
                    votes_per_candidate={
                        CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 19,
                        CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 3,
                    },
                )
            },
        ),
    ),
    (
        "./test/data/neighbourhood_files/valid.csv",
        {"SB1": "1234AB", "SB2": "1235AB", "SB3": "9999XX", "SB4": None},
        {
            "SB1": ReportingUnitInfo(
                reporting_unit_id="SB1",
                reporting_unit_name="Stembureau StAtIoN NS dorpsstraat",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 10},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 8,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 2,
                },
            ),
            "SB2": ReportingUnitInfo(
                reporting_unit_id="SB2",
                reporting_unit_name=None,
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 12},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 11,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 1,
                },
            ),
            "SB3": ReportingUnitInfo(
                reporting_unit_id="SB3",
                reporting_unit_name="SB3",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 100},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 80,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 20,
                },
            ),
            "SB4": ReportingUnitInfo(
                reporting_unit_id="SB4",
                reporting_unit_name="SB4",
                cast=0,
                total_counted=0,
                rejected_votes={},
                uncounted_votes={},
                votes_per_party={PartyIdentifier(id=1, name=None): 200},
                votes_per_candidate={
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 160,
                    CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 40,
                },
            ),
        },
        ReportingNeighbourhoods(
            reporting_unit_id_to_neighbourhood_id={
                "SB1": None,
                "SB2": "WK123",
                "SB3": None,
                "SB4": None,
            },
            neighbourhood_id_to_reporting_unit_ids={"WK123": set(["SB2"])},
            neighbourhood_id_to_reference_group={
                "WK123": ReportingUnitInfo(
                    reporting_unit_id="WK123",
                    reporting_unit_name="Reference group for WK123",
                    cast=0,
                    total_counted=0,
                    rejected_votes={},
                    uncounted_votes={},
                    votes_per_party={PartyIdentifier(id=1, name=None): 12},
                    votes_per_candidate={
                        CandidateIdentifier(PartyIdentifier(id=1, name=None), 1): 11,
                        CandidateIdentifier(PartyIdentifier(id=1, name=None), 2): 1,
                    },
                )
            },
        ),
    ),
]


@pytest.mark.parametrize(
    "path_to_read, reporting_unit_zips, reporting_unit_info, expected",
    reporting_neighbourhoods_test_cases,
)
def test_fetch_reporting_neighbourhoods(
    path_to_read: str,
    reporting_unit_zips: Dict[str, Optional[str]],
    reporting_unit_info: Dict[str, ReportingUnitInfo],
    expected: ReportingNeighbourhoods,
) -> None:
    neighbourhood_data = NeighbourhoodData.from_path(path_to_read)
    assert neighbourhood_data is not None
    reporting_neighourhoods = neighbourhood_data.fetch_reporting_neighbourhoods(
        reporting_unit_zips, reporting_unit_info
    )
    assert reporting_neighourhoods == expected


def construct_reporting_unit(id: str) -> ReportingUnitInfo:
    return ReportingUnitInfo(
        reporting_unit_id=id,
        reporting_unit_name=id,
        cast=0,
        total_counted=0,
        rejected_votes={},
        uncounted_votes={},
        votes_per_party={},
        votes_per_candidate={},
    )


reporting_unit_data = ReportingNeighbourhoods(
    reporting_unit_id_to_neighbourhood_id={"a": "1", "b": "2", "c": "2", "d": None},
    neighbourhood_id_to_reporting_unit_ids={"1": set(["a"]), "2": set(["b", "c"])},
    neighbourhood_id_to_reference_group={
        "1": construct_reporting_unit("ref_a"),
        "2": construct_reporting_unit("ref_b_c"),
    },
)

reference_group_test_cases = zip(
    repeat(reporting_unit_data),
    ["a", "b", "d"],
    [construct_reporting_unit("ref_a"), construct_reporting_unit("ref_b_c"), None],
)
reference_size_test_cases = zip(repeat(reporting_unit_data), ["a", "b", "d"], [1, 2, 0])


@pytest.mark.parametrize(
    "reporting_neighbourhoods, reporting_unit_id, expected",
    reference_group_test_cases,
)
def test_reporting_neighbourhoods_reference_group(
    reporting_neighbourhoods: ReportingNeighbourhoods,
    reporting_unit_id: str,
    expected: Optional[ReportingUnitInfo],
):
    assert reporting_neighbourhoods.get_reference_group(reporting_unit_id) == expected


@pytest.mark.parametrize(
    "reporting_neighbourhoods, reporting_unit_id, expected",
    reference_size_test_cases,
)
def test_reporting_neighbourhoods_size(
    reporting_neighbourhoods: ReportingNeighbourhoods,
    reporting_unit_id: str,
    expected: Optional[ReportingUnitInfo],
):
    assert reporting_neighbourhoods.get_reference_size(reporting_unit_id) == expected
