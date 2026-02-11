from itertools import repeat
from typing import Dict, List, Optional

import pytest

from hcp import protocol_checks
from hcp.eml_types import (
    CandidateIdentifier,
    PartyIdentifier,
    ReportingUnitInfo,
    SwitchedCandidate,
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
        [expected_switched_candidates, None, [], []],
        [10, 4, 10, 10],
        [1, 5, 5, 5],
        [4, 4, 5, 4],
        [4, 4, 4, 5],
        [None, None, None, None]
    )
)

@pytest.mark.parametrize(
    "main_unit, reporting_unit, expected, amount_of_reporting_units, minimum_reporting_units, minimum_deviation_factor, minimum_votes, max_rmse",
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
    max_rmse
) -> None:
    assert (
        protocol_checks._get_potentially_switched_candidates(
            main_unit,
            reporting_unit,
            amount_of_reporting_units,
            minimum_reporting_units,
            minimum_deviation_factor,
            minimum_votes,
            max_rmse
        )
        == expected
    )

#### High RMSE test case
high_rmse_switched_main_unit = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=0,
    rejected_votes={},
    uncounted_votes={},
    votes_per_party={PartyIdentifier(1, None): 2350},
    votes_per_candidate={
        CandidateIdentifier(PartyIdentifier(1, None), 1): 1000,
        CandidateIdentifier(PartyIdentifier(1, None), 2): 200,
        CandidateIdentifier(PartyIdentifier(1, None), 3): 50,
        CandidateIdentifier(PartyIdentifier(1, None), 4): 300,
        CandidateIdentifier(PartyIdentifier(1, None), 5): 800,
    },
)

high_rmse_switched_reporting_unit = ReportingUnitInfo(
    reporting_unit_id=None,
    reporting_unit_name=None,
    cast=0,
    total_counted=0,
    rejected_votes={},
    uncounted_votes={},
    votes_per_party={PartyIdentifier(1, None): 233},
    votes_per_candidate={
        CandidateIdentifier(PartyIdentifier(1, None), 1): 95,
        CandidateIdentifier(PartyIdentifier(1, None), 2): 80,
        CandidateIdentifier(PartyIdentifier(1, None), 3): 6,
        CandidateIdentifier(PartyIdentifier(1, None), 4): 32,
        CandidateIdentifier(PartyIdentifier(1, None), 5): 20,
    },
)

def test_high_rmse_switched_candidate():
    no_rmse_filter = protocol_checks._get_potentially_switched_candidates(
        high_rmse_switched_main_unit,
        high_rmse_switched_reporting_unit,
        20,
        10,
        4,
        20,
        None
    )
    assert no_rmse_filter == [SwitchedCandidate(
        candidate_with_fewer=CandidateIdentifier(PartyIdentifier(1, None), 5),
        candidate_with_fewer_expected=86,
        candidate_with_fewer_received=20,
        candidate_with_more=CandidateIdentifier(PartyIdentifier(1, None), 2),
        candidate_with_more_expected=13,
        candidate_with_more_received=80,
    )]

    rmse_filter = protocol_checks._get_potentially_switched_candidates(
        high_rmse_switched_main_unit,
        high_rmse_switched_reporting_unit,
        20,
        10,
        4,
        20,
        3.0
    )

    # Actual RMSE of this test case is 3.1, so the check did run, but returned no results
    # since we set an upper limit of 3.0.
    assert(rmse_filter == [])

###

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
