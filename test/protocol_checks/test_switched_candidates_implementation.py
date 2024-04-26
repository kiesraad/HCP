from itertools import repeat
from typing import Dict, List, Optional

import protocol_checks
import pytest
from eml_types import (
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
