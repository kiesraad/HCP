import protocol_checks
import pytest
from eml_types import ReportingUnitInfo
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
    "data, kind, expected",
    [
        (ru_1pc_blank_votes, "blanco", False),
        (ru_3pc_blank_votes, "blanco", True),
        (ru_1pc_invalid_votes, "ongeldig", False),
        (ru_3pc_invalid_votes, "ongeldig", True),
    ],
)
def test_check_too_many_rejected_votes(
    data: ReportingUnitInfo, kind: str, expected: bool
) -> None:
    assert protocol_checks.check_too_many_rejected_votes(data, kind) == expected


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
    "data, expected", [(ru_2pc_explained_differences, True), (ru_zero_votes, False)]
)
def test_check_too_many_explained_differences(
    data: ReportingUnitInfo, expected: bool
) -> None:
    assert protocol_checks.check_too_many_explained_differences(data) == expected


mu_50_pct_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=218,
    rejected_votes={"ongeldig": 20, "blanco": 10},
    uncounted_votes={"meegenomen stembiljetten": 1, "andere verklaring": 1},
    votes_per_party={"A": 118, "B": 50, "C": 50},
)

ru_50_pct_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=22,
    rejected_votes={"ongeldig": 20, "blanco": 20},
    uncounted_votes={"meegenomen stembiljetten": 1, "andere verklaring": 0},
    votes_per_party={"A": 2, "B": 10, "C": 10},
)

ru_46_pct_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=23,
    rejected_votes={"ongeldig": 20, "blanco": 20},
    uncounted_votes={"meegenomen stembiljetten": 1, "andere verklaring": 0},
    votes_per_party={"A": 3, "B": 10, "C": 10},
)


@pytest.mark.parametrize(
    "main_unit, reporting_unit, expected",
    [
        (mu_50_pct_difference, ru_50_pct_difference, ["A"]),
        (mu_50_pct_difference, ru_46_pct_difference, []),
    ],
)
def test_check_parties_with_large_percentage_difference(
    main_unit: ReportingUnitInfo, reporting_unit: ReportingUnitInfo, expected: List[str]
) -> None:
    assert (
        protocol_checks.check_parties_with_large_percentage_difference(
            main_unit, reporting_unit
        )
        == expected
    )
