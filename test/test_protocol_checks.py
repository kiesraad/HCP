import protocol_checks
import pytest
from eml_types import ReportingUnitInfo, PartyIdentifier
from typing import List

ru_zero_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=0,
    rejected_votes={"ongeldig": 0, "blanco": 0},
    uncounted_votes={},
    votes_per_party={},
)

ru_some_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=1_000_000,
    rejected_votes={"ongeldig": 1, "blanco": 2},
    uncounted_votes={},
    votes_per_party={},
)


@pytest.mark.parametrize(
    "data, expected", [(ru_zero_votes, True), (ru_some_votes, False)]
)
def test_check_zero_votes(data: ReportingUnitInfo, expected: bool) -> None:
    assert protocol_checks.check_zero_votes(data) == expected


ru_two_inexplicable_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=1_000_000,
    rejected_votes={"ongeldig": 1, "blanco": 2},
    uncounted_votes={"geen verklaring": 2},
    votes_per_party={},
)

ru_zero_inexplicable_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=1_000_000,
    rejected_votes={"ongeldig": 1, "blanco": 2},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
)


@pytest.mark.parametrize(
    "data, expected",
    [(ru_two_inexplicable_difference, 2), (ru_zero_inexplicable_difference, 0)],
)
def test_check_inexplicable_difference(data: ReportingUnitInfo, expected: int) -> None:
    assert protocol_checks.check_inexplicable_difference(data) == expected


ru_3pc_invalid_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=97,
    rejected_votes={"ongeldig": 3, "blanco": 0},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
)

ru_1pc_invalid_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=99,
    rejected_votes={"ongeldig": 1, "blanco": 0},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
)

ru_3pc_blank_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=97,
    rejected_votes={"ongeldig": 0, "blanco": 3},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
)

ru_1pc_blank_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=99,
    rejected_votes={"ongeldig": 0, "blanco": 1},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
)


@pytest.mark.parametrize(
    "data, kind, threshold_pct, expected",
    [
        (ru_1pc_blank_votes, "blanco", 3.0, False),
        (ru_3pc_blank_votes, "blanco", 3.0, True),
        (ru_1pc_invalid_votes, "ongeldig", 3.0, False),
        (ru_3pc_invalid_votes, "ongeldig", 3.0, True),
    ],
)
def test_check_too_many_rejected_votes(
    data: ReportingUnitInfo, kind: str, threshold_pct: float, expected: bool
) -> None:
    assert (
        protocol_checks.check_too_many_rejected_votes(data, kind, threshold_pct)
        == expected
    )


ru_2pc_explained_differences = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=94,
    rejected_votes={"ongeldig": 2, "blanco": 2},
    uncounted_votes={"meegenomen stembiljetten": 1, "andere verklaring": 1},
    votes_per_party={},
)


@pytest.mark.parametrize(
    "data, threshold_pct, expected",
    [(ru_2pc_explained_differences, 2.0, True), (ru_zero_votes, 2.0, False)],
)
def test_check_too_many_explained_differences(
    data: ReportingUnitInfo, threshold_pct: float, expected: bool
) -> None:
    assert (
        protocol_checks.check_too_many_explained_differences(data, threshold_pct)
        == expected
    )


mu_50_pct_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=218,
    rejected_votes={"ongeldig": 20, "blanco": 10},
    uncounted_votes={"meegenomen stembiljetten": 1, "andere verklaring": 1},
    votes_per_party={
        PartyIdentifier(1, None): 118,
        PartyIdentifier(2, "B"): 50,
        PartyIdentifier(3, "C"): 50,
    },
)

ru_50_pct_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=22,
    rejected_votes={"ongeldig": 20, "blanco": 20},
    uncounted_votes={"meegenomen stembiljetten": 1, "andere verklaring": 0},
    votes_per_party={
        PartyIdentifier(1, None): 2,
        PartyIdentifier(2, "B"): 10,
        PartyIdentifier(3, "C"): 10,
    },
)

ru_46_pct_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=23,
    rejected_votes={"ongeldig": 20, "blanco": 20},
    uncounted_votes={"meegenomen stembiljetten": 1, "andere verklaring": 0},
    votes_per_party={
        PartyIdentifier(1, None): 3,
        PartyIdentifier(2, "B"): 10,
        PartyIdentifier(3, "C"): 10,
    },
)


@pytest.mark.parametrize(
    "main_unit, reporting_unit, threshold_pct, expected",
    [
        (mu_50_pct_difference, ru_50_pct_difference, 50.0, ["1. blanco"]),
        (mu_50_pct_difference, ru_46_pct_difference, 50.0, []),
    ],
)
def test_check_parties_with_large_percentage_difference(
    main_unit: ReportingUnitInfo,
    reporting_unit: ReportingUnitInfo,
    threshold_pct: float,
    expected: List[str],
) -> None:
    assert (
        protocol_checks.check_parties_with_large_percentage_difference(
            main_unit, reporting_unit, threshold_pct
        )
        == expected
    )


sum_difference_testcases = [
    (
        ReportingUnitInfo(
            reporting_unit_id=None,
            reporting_unit_name=None,
            cast=100,
            total_counted=97,
            rejected_votes={"ongeldig": 1, "blanco": 2},
            uncounted_votes={
                "toegelaten kiezers": 90,
                "minder getelde stembiljetten": 0,
                "meer getelde stembiljetten": 10,
                "te veel uitgereikte stembiljetten": 1,
                "te veel briefstembiljetten": 1,
                "geen verklaring": 1,
                "andere verklaring": 2,
            },
            votes_per_party={},
        ),
        5,
    ),
    (
        ReportingUnitInfo(
            reporting_unit_id=None,
            reporting_unit_name=None,
            cast=100,
            total_counted=97,
            rejected_votes={"ongeldig": 1, "blanco": 2},
            uncounted_votes={
                "toegelaten kiezers": 110,
                "minder getelde stembiljetten": 10,
                "meer getelde stembiljetten": 0,
                "meegenomen stembiljetten": 1,
                "te weinig uitgereikte stembiljetten": 1,
                "geen briefstembiljetten": 1,
                "kwijtgeraakte stembiljetten": 1,
                "geen verklaring": 2,
                "andere verklaring": 1,
            },
            votes_per_party={},
        ),
        -3,
    ),
    (
        ReportingUnitInfo(
            reporting_unit_id=None,
            reporting_unit_name=None,
            cast=100,
            total_counted=97,
            rejected_votes={"ongeldig": 1, "blanco": 2},
            uncounted_votes={
                "toegelaten kiezers": 100,
                "minder getelde stembiljetten": 1,
                "meer getelde stembiljetten": 1,
                "meegenomen stembiljetten": 0,
                "te weinig uitgereikte stembiljetten": 0,
                "te veel uitgereikte stembiljetten": 0,
                "geen briefstembiljetten": 0,
                "kwijtgeraakte stembiljetten": 0,
                "geen verklaring": 0,
                "andere verklaring": 0,
            },
            votes_per_party={},
        ),
        0,
    ),
]


@pytest.mark.parametrize(
    "reporting_unit, expected_difference", sum_difference_testcases
)
def test_check_explanation_sum_difference(
    reporting_unit: ReportingUnitInfo, expected_difference: int
) -> None:
    assert (
        protocol_checks.check_explanation_sum_difference(reporting_unit)
        == expected_difference
    )
