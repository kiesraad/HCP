from itertools import repeat
from typing import Dict, List, Optional

import protocol_checks
import pytest
from eml_types import (
    CandidateIdentifier,
    PartyIdentifier,
    ReportingUnitInfo,
    SwitchedCandidate,
    VoteDifferenceAmount,
    VoteDifferencePercentage,
)

ru_zero_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=0,
    rejected_votes={"ongeldig": 0, "blanco": 0},
    uncounted_votes={},
    votes_per_party={},
    votes_per_candidate={},
)

ru_some_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=1_000_000,
    rejected_votes={"ongeldig": 1, "blanco": 2},
    uncounted_votes={},
    votes_per_party={},
    votes_per_candidate={},
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
    votes_per_candidate={},
)

ru_zero_inexplicable_difference = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=1_000_000,
    rejected_votes={"ongeldig": 1, "blanco": 2},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
    votes_per_candidate={},
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
    votes_per_candidate={},
)

ru_1pc_invalid_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=99,
    rejected_votes={"ongeldig": 1, "blanco": 0},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
    votes_per_candidate={},
)

ru_3pc_blank_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=97,
    rejected_votes={"ongeldig": 0, "blanco": 3},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
    votes_per_candidate={},
)

ru_1pc_blank_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=99,
    rejected_votes={"ongeldig": 0, "blanco": 1},
    uncounted_votes={"geen verklaring": 0},
    votes_per_party={},
    votes_per_candidate={},
)


@pytest.mark.parametrize(
    "data, kind, threshold_pct, expected",
    [
        (ru_1pc_blank_votes, "blanco", 3.0, None),
        (ru_3pc_blank_votes, "blanco", 3.0, 3.0),
        (ru_1pc_invalid_votes, "ongeldig", 3.0, None),
        (ru_3pc_invalid_votes, "ongeldig", 3.0, 3.0),
    ],
)
def test_check_too_many_rejected_votes(
    data: ReportingUnitInfo, kind: str, threshold_pct: float, expected: bool
) -> None:
    assert (
        protocol_checks.check_too_many_rejected_votes(data, kind, threshold_pct)
        == expected
    )


def test_check_invalid_kind_passed_too_many_rejected_votes():
    ru = ReportingUnitInfo(None, None, 0, 0, {}, {}, {}, {})
    with pytest.raises(ValueError):
        protocol_checks.check_too_many_rejected_votes(ru, "INVALID_KIND", 0)


ru_2pc_differences = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=94,
    rejected_votes={"ongeldig": 2, "blanco": 2},
    uncounted_votes={
        "toegelaten kiezers": 92,
        "meegenomen stembiljetten": 1,
        "andere verklaring": 1,
    },
    votes_per_party={},
    votes_per_candidate={},
)

ru_5_lost_votes = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=110,
    rejected_votes={"ongeldig": 1, "blanco": 0},
    uncounted_votes={
        "toegelaten kiezers": 116,
        "geen verklaring": 3,
        "te weinig uitgereikte stembiljetten": 2,
    },
    votes_per_party={},
    votes_per_candidate={},
)


@pytest.mark.parametrize(
    "data, threshold_pct, threshold, expected",
    [
        (
            ru_2pc_differences,
            2.0,
            10,
            VoteDifferencePercentage(value=6 / 98 * 100),
        ),
        (ru_zero_votes, 2.0, 10, None),
        (ru_5_lost_votes, 5.0, 5, VoteDifferenceAmount(value=5)),
    ],
)
def test_check_too_many_differences(
    data: ReportingUnitInfo, threshold_pct: float, threshold: int, expected: bool
) -> None:
    assert (
        protocol_checks.check_too_many_differences(data, threshold_pct, threshold)
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
    votes_per_candidate={},
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
    votes_per_candidate={},
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
    votes_per_candidate={},
)


@pytest.mark.parametrize(
    "main_unit, reporting_unit, threshold_pct, expected",
    [
        (mu_50_pct_difference, ru_50_pct_difference, 50.0, ["1. blanco (-50%)"]),
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
            votes_per_candidate={},
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
            votes_per_candidate={},
        ),
        3,
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
            votes_per_candidate={},
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


switched_main_unit = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=0,
    rejected_votes={},
    uncounted_votes={},
    votes_per_party={PartyIdentifier(1, None): 101},
    votes_per_candidate={
        CandidateIdentifier(PartyIdentifier(1, None), 1): 40,
        CandidateIdentifier(PartyIdentifier(1, None), 2): 30,
        CandidateIdentifier(PartyIdentifier(1, None), 3): 20,
        CandidateIdentifier(PartyIdentifier(1, None), 4): 10,
        CandidateIdentifier(PartyIdentifier(1, None), 5): 1,
    },
)

expected_reporting_unit = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=0,
    rejected_votes={},
    uncounted_votes={},
    votes_per_party={PartyIdentifier(1, None): 11},
    votes_per_candidate={
        CandidateIdentifier(PartyIdentifier(1, None), 1): 1,
        CandidateIdentifier(PartyIdentifier(1, None), 2): 2,
        CandidateIdentifier(PartyIdentifier(1, None), 3): 3,
        CandidateIdentifier(PartyIdentifier(1, None), 4): 4,
        CandidateIdentifier(PartyIdentifier(1, None), 5): 1,
    },
)

expected_cand_votes = {
    CandidateIdentifier(PartyIdentifier(1, None), 1): ((40 - 1) / 90) * 11,
    CandidateIdentifier(PartyIdentifier(1, None), 2): ((30 - 2) / 90) * 11,
    CandidateIdentifier(PartyIdentifier(1, None), 3): ((20 - 3) / 90) * 11,
    CandidateIdentifier(PartyIdentifier(1, None), 4): ((10 - 4) / 90) * 11,
    CandidateIdentifier(PartyIdentifier(1, None), 5): 0,
}


@pytest.mark.parametrize(
    "main_unit, reporting_unit, expected",
    [(switched_main_unit, expected_reporting_unit, expected_cand_votes)],
)
def test_get_expected_candidate_votes(
    main_unit: ReportingUnitInfo,
    reporting_unit: ReportingUnitInfo,
    expected: Dict[CandidateIdentifier, float],
) -> None:
    assert (
        protocol_checks._get_expected_candidate_votes(main_unit, reporting_unit)
        == expected
    )


switched_reporting_unit = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=0,
    rejected_votes={},
    uncounted_votes={},
    votes_per_party={PartyIdentifier(1, None): 10},
    votes_per_candidate={
        CandidateIdentifier(PartyIdentifier(1, None), 1): 1,
        CandidateIdentifier(PartyIdentifier(1, None), 2): 3,
        CandidateIdentifier(PartyIdentifier(1, None), 3): 2,
        CandidateIdentifier(PartyIdentifier(1, None), 4): 4,
        CandidateIdentifier(PartyIdentifier(1, None), 5): 0,
    },
)

expected_switched_candidates = [
    SwitchedCandidate(
        candidate_with_fewer=CandidateIdentifier(PartyIdentifier(1, None), 1),
        candidate_with_fewer_expected=4,
        candidate_with_fewer_received=1,
        candidate_with_more=CandidateIdentifier(PartyIdentifier(1, None), 4),
        candidate_with_more_expected=1,
        candidate_with_more_received=4,
    )
]

switched_test_cases = list(
    zip(
        repeat(switched_main_unit),
        repeat(switched_reporting_unit),
        [expected_switched_candidates, [], [], []],
        [10, 4, 10, 10],
        [1, 5, 5, 5],
        [4, 4, 5, 4],
        [4, 4, 4, 5],
    )
)


@pytest.mark.parametrize(
    "main_unit, reporting_unit, expected, amount_of_reporting_units, minimum_reporting_units, minimum_deviation_factor, minimum_votes",
    switched_test_cases,
)
def test_get_switched_candidate(
    main_unit,
    reporting_unit,
    expected,
    amount_of_reporting_units,
    minimum_reporting_units,
    minimum_deviation_factor,
    minimum_votes,
) -> None:
    assert (
        protocol_checks._get_potentially_switched_candidates(
            main_unit,
            reporting_unit,
            amount_of_reporting_units,
            minimum_reporting_units,
            minimum_deviation_factor,
            minimum_votes,
        )
        == expected
    )


combine_switched_testcases = [
    (
        [
            SwitchedCandidate(
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 1),
                0,
                10,
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 2),
                10,
                0,
            )
        ],
        [
            SwitchedCandidate(
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 1),
                0,
                2,
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 2),
                3,
                0,
            ),
            SwitchedCandidate(
                CandidateIdentifier(PartyIdentifier(5, None), 10),
                1,
                101,
                CandidateIdentifier(PartyIdentifier(5, None), 8),
                108,
                1,
            ),
        ],
        [
            SwitchedCandidate(
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 1),
                0,
                10,
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 2),
                10,
                0,
            ),
            SwitchedCandidate(
                CandidateIdentifier(PartyIdentifier(5, None), 10),
                1,
                101,
                CandidateIdentifier(PartyIdentifier(5, None), 8),
                108,
                1,
            ),
        ],
    ),
    (
        [
            SwitchedCandidate(
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 1),
                0,
                10,
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 2),
                10,
                0,
            )
        ],
        None,
        [
            SwitchedCandidate(
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 1),
                0,
                10,
                CandidateIdentifier(PartyIdentifier(1, "Lijst 1"), 2),
                10,
                0,
            )
        ],
    ),
]


@pytest.mark.parametrize(
    "switched_municipality, switched_neighbourhood, expected",
    combine_switched_testcases,
)
def test_get_switched_candidate_combination(
    switched_municipality: List[SwitchedCandidate],
    switched_neighbourhood: Optional[List[SwitchedCandidate]],
    expected: List[SwitchedCandidate],
) -> None:
    assert (
        protocol_checks._get_switched_candidate_combination(
            switched_municipality, switched_neighbourhood
        )
        == expected
    )
