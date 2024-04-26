from collections import defaultdict
from typing import Dict, List

import protocol_checks
from eml_types import (
    CandidateIdentifier,
    PartyIdentifier,
    ReportingUnitInfo,
    SwitchedCandidate,
    SwitchedCandidateConfig,
)
from neighbourhood import ReportingNeighbourhoods

# Helper functions to easily create testing datasets


def _create_candidate_votes(
    party_ids: List[int], votes: List[int]
) -> Dict[CandidateIdentifier, int]:
    cand_ids = defaultdict(int)

    result = {}
    for party_id, votecount in zip(party_ids, votes):
        cand_ids[party_id] += 1
        result[
            CandidateIdentifier(PartyIdentifier(party_id, None), cand_ids[party_id])
        ] = votecount

    return result


def _create_party_votes(
    cand_votes: Dict[CandidateIdentifier, int]
) -> Dict[PartyIdentifier, int]:
    result = defaultdict(int)
    for cand_id, votes in cand_votes.items():
        result[cand_id.party] += votes
    return result


def _create_ru(id: str, party_ids: List[int], votes: List[int]) -> ReportingUnitInfo:
    votes_per_candidate = _create_candidate_votes(party_ids, votes)
    return ReportingUnitInfo(
        reporting_unit_id=id,
        reporting_unit_name=None,
        cast=0,
        total_counted=0,
        rejected_votes={},
        uncounted_votes={},
        votes_per_candidate=votes_per_candidate,
        votes_per_party=_create_party_votes(votes_per_candidate),
    )


def _create_mu(reporting_units: List[ReportingUnitInfo]) -> ReportingUnitInfo:
    cands = list(reporting_units[0].votes_per_candidate.keys())
    candidate_votes = {
        cand_id: sum([ru.votes_per_candidate[cand_id] for ru in reporting_units])
        for cand_id in cands
    }
    party_votes = _create_party_votes(candidate_votes)
    return ReportingUnitInfo(
        reporting_unit_id="mu",
        reporting_unit_name=None,
        cast=0,
        total_counted=0,
        rejected_votes={},
        uncounted_votes={},
        votes_per_candidate=candidate_votes,
        votes_per_party=party_votes,
    )


# First we test a few cases where we do not have any neighbourhood information

# Cand 1 and 2 of party 1 in reporting unit 1 have been switched (with a deviation ~2.0)
case_1_ru = [
    _create_ru("1", [1, 1, 2, 2], [20, 10, 10, 20]),
    _create_ru("2", [1, 1, 2, 2], [11, 19, 10, 20]),
    _create_ru("3", [1, 1, 2, 2], [9, 24, 10, 20]),
    _create_ru("4", [1, 1, 2, 2], [120, 250, 10, 20]),
]
case_1_mu = _create_mu(case_1_ru)
case_1_config = SwitchedCandidateConfig(
    minimum_reporting_units_municipality=4,
    minimum_reporting_units_neighbourhood=1,
    minimum_deviation_factor=2,
    minimum_votes=5,
)
case_1_expected = [
    SwitchedCandidate(
        candidate_with_fewer=CandidateIdentifier(PartyIdentifier(1, None), 2),
        candidate_with_fewer_expected=20,
        candidate_with_fewer_received=10,
        candidate_with_more=CandidateIdentifier(PartyIdentifier(1, None), 1),
        candidate_with_more_expected=10,
        candidate_with_more_received=20,
    )
]


def test_case_1():
    assert (
        protocol_checks.check_potentially_switched_candidates(
            polling_station_id="1",
            main_unit=case_1_mu,
            polling_station=case_1_ru[0],
            reporting_unit_amount=len(case_1_ru),
            reporting_neighbourhoods=None,
            config=case_1_config,
        )
        == case_1_expected
    )


## Special case with neighbourhood info and two reporting units, both reporting units contain a switch,
## since they are only compared to the other. If we did not use neighbourhood info, only report unit
## with id "2" would have contained a switch.

case_2_ru = [
    _create_ru("1", [1, 1, 2, 2], [100, 200, 20, 20]),
    _create_ru("2", [1, 1, 2, 2], [21, 9, 10, 20]),
    _create_ru("3", [1, 1, 2, 2], [9, 24, 10, 20]),
    _create_ru("4", [1, 1, 2, 2], [120, 250, 10, 20]),
]
case_2_mu = _create_mu(case_2_ru)
case_2_config = SwitchedCandidateConfig(
    minimum_reporting_units_municipality=4,
    minimum_reporting_units_neighbourhood=1,
    minimum_deviation_factor=2,
    minimum_votes=5,
)

reporting_neighbourhoods = ReportingNeighbourhoods(
    reporting_unit_id_to_neighbourhood_id={"1": "a", "2": "a", "3": "b", "4": None},
    neighbourhood_id_to_reporting_unit_ids={"a": set(["1", "2"]), "b": set(["3"])},
    neighbourhood_id_to_reference_group={
        "a": _create_mu([case_2_ru[0], case_2_ru[1]]),
        "b": _create_mu([case_2_ru[2]]),
    },
)


def test_case_2():
    result = protocol_checks.check_potentially_switched_candidates(
        polling_station_id="1",
        main_unit=case_2_mu,
        polling_station=case_2_ru[0],
        reporting_unit_amount=len(case_2_ru),
        reporting_neighbourhoods=reporting_neighbourhoods,
        config=case_2_config,
    )
    assert result == [
        SwitchedCandidate(
            candidate_with_fewer=CandidateIdentifier(
                party=PartyIdentifier(id=1, name=None), cand_id=1
            ),
            candidate_with_fewer_received=100,
            candidate_with_fewer_expected=210,
            candidate_with_more=CandidateIdentifier(
                party=PartyIdentifier(id=1, name=None), cand_id=2
            ),
            candidate_with_more_received=200,
            candidate_with_more_expected=90,
        )
    ]

    result = protocol_checks.check_potentially_switched_candidates(
        polling_station_id="2",
        main_unit=case_2_mu,
        polling_station=case_2_ru[1],
        reporting_unit_amount=len(case_2_ru),
        reporting_neighbourhoods=reporting_neighbourhoods,
        config=case_2_config,
    )
    assert result == [
        SwitchedCandidate(
            candidate_with_fewer=CandidateIdentifier(
                party=PartyIdentifier(id=1, name=None), cand_id=2
            ),
            candidate_with_fewer_received=9,
            candidate_with_fewer_expected=20,
            candidate_with_more=CandidateIdentifier(
                party=PartyIdentifier(id=1, name=None), cand_id=1
            ),
            candidate_with_more_received=21,
            candidate_with_more_expected=10,
        )
    ]
