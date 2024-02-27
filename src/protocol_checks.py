from itertools import product as cartesian_product
from typing import Dict, List, Optional, TypeVar

from eml_types import (
    CandidateIdentifier,
    PartyIdentifier,
    ReportingUnitInfo,
    SwitchedCandidate,
    SwitchedCandidateConfig,
    VoteDifference,
    VoteDifferenceAmount,
    VoteDifferencePercentage,
)
from neighbourhood import ReportingNeighbourhoods

T = TypeVar("T")
N = TypeVar("N", int, float)


def check_zero_votes(reporting_unit: ReportingUnitInfo) -> bool:
    return _get_total_votes(reporting_unit) == 0


def check_inexplicable_difference(reporting_unit: ReportingUnitInfo) -> int:
    return reporting_unit.uncounted_votes["geen verklaring"]


def check_explanation_sum_difference(reporting_unit: ReportingUnitInfo) -> int:
    vote_metadata = reporting_unit.uncounted_votes

    vote_difference = (
        _get_total_votes(reporting_unit) - vote_metadata["toegelaten kiezers"]
    )

    if vote_difference > 0:
        return abs(
            vote_difference
            - (vote_metadata.get("te veel uitgereikte stembiljetten") or 0)
            - (vote_metadata.get("te veel briefstembiljetten") or 0)
            - (vote_metadata.get("geen verklaring") or 0)
            - (vote_metadata.get("andere verklaring") or 0)
        )

    if vote_difference < 0:
        return abs(
            vote_difference
            + (vote_metadata.get("meegenomen stembiljetten") or 0)
            + (vote_metadata.get("te weinig uitgereikte stembiljetten") or 0)
            + (vote_metadata.get("geen briefstembiljetten") or 0)
            + (vote_metadata.get("kwijtgeraakte stembiljetten") or 0)
            + (vote_metadata.get("geen verklaring") or 0)
            + (vote_metadata.get("andere verklaring") or 0)
        )

    return 0


def check_too_many_rejected_votes(
    reporting_unit: ReportingUnitInfo, kind: str, threshold_pct: float
) -> Optional[float]:
    if kind not in ["ongeldig", "blanco"]:
        raise ValueError(f"Invalid rejected vote kind passed: {kind}")

    rejected_votes = reporting_unit.rejected_votes[kind]
    total_votes = _get_total_votes(reporting_unit)
    percentage = _percentage(rejected_votes, total_votes)

    return percentage if percentage and percentage >= threshold_pct else None


def check_too_many_differences(
    reporting_unit: ReportingUnitInfo, threshold_pct: float, threshold: int
) -> Optional[VoteDifference]:
    differences = _get_differences(reporting_unit)
    total_votes = _get_total_votes(reporting_unit)
    percentage = _percentage(differences, total_votes)

    if differences >= threshold:
        return VoteDifferenceAmount(value=differences)

    if percentage and percentage >= threshold_pct:
        return VoteDifferencePercentage(value=percentage)

    return None


def get_party_difference_percentages(
    main_unit: ReportingUnitInfo, reporting_unit: ReportingUnitInfo
) -> Dict[PartyIdentifier, float]:
    global_total = main_unit.total_counted - reporting_unit.total_counted
    global_party = _subtract_part_dictionary(
        main_unit.votes_per_party, reporting_unit.votes_per_party
    )
    global_percentages = _get_percentages(global_party, global_total)
    local_percentages = _get_percentages(
        reporting_unit.votes_per_party, reporting_unit.total_counted
    )
    difference = _subtract_part_dictionary(local_percentages, global_percentages)

    return difference


def check_parties_with_large_percentage_difference(
    main_unit: ReportingUnitInfo,
    reporting_unit: ReportingUnitInfo,
    threshold_pct: float,
) -> List[str]:
    differences = get_party_difference_percentages(main_unit, reporting_unit)
    return sorted(
        [
            (
                f"{identifier.name} ({int(difference)}%)"
                if identifier.name
                else f"{identifier.id}. blanco ({int(difference)}%)"
            )
            for (identifier, difference) in differences.items()
            if abs(difference) >= threshold_pct
        ]
    )


def check_potentially_switched_candidates(
    polling_station_id: str,
    main_unit: ReportingUnitInfo,
    polling_station: ReportingUnitInfo,
    reporting_unit_amount: int,
    reporting_neighbourhoods: Optional[ReportingNeighbourhoods],
    config: SwitchedCandidateConfig,
) -> List[SwitchedCandidate]:
    neighbourhood_reference_group = (
        (reporting_neighbourhoods.get_reference_group(polling_station_id))
        if reporting_neighbourhoods
        else None
    )

    potentially_switched_municipality_candidates = _get_potentially_switched_candidates(
        main_unit,
        polling_station,
        amount_of_reporting_units=reporting_unit_amount,
        minimum_reporting_units=config.minimum_reporting_units_municipality,
        minimum_deviation_factor=config.minimum_deviation_factor,
        minimum_votes=config.minimum_votes,
    )

    potentially_switched_neighbourhood_candidates = (
        _get_potentially_switched_candidates(
            neighbourhood_reference_group,
            polling_station,
            amount_of_reporting_units=reporting_neighbourhoods.get_reference_size(
                polling_station_id
            ),
            minimum_reporting_units=config.minimum_reporting_units_neighbourhood,
            minimum_deviation_factor=config.minimum_deviation_factor,
            minimum_votes=config.minimum_votes,
        )
        if neighbourhood_reference_group and reporting_neighbourhoods
        else None
    )

    return _get_switched_candidate_combination(
        potentially_switched_municipality_candidates,
        potentially_switched_neighbourhood_candidates,
    )


# Implementation details


def _get_total_votes(reporting_unit: ReportingUnitInfo) -> int:
    rejected_votes = reporting_unit.rejected_votes
    return (
        reporting_unit.total_counted
        + rejected_votes["ongeldig"]
        + rejected_votes["blanco"]
    )


def _get_differences(reporting_unit: ReportingUnitInfo) -> int:
    admitted_voters = reporting_unit.uncounted_votes.get("toegelaten kiezers") or 0
    total_votes = _get_total_votes(reporting_unit)

    return abs(total_votes - admitted_voters)


def _percentage(part: int, total: int) -> Optional[float]:
    try:
        return part / total * 100
    except ZeroDivisionError:
        return None


def _get_percentages(dictionary: Dict[T, int], total: int) -> Dict[T, float]:
    return_dict = {}
    for key in dictionary.keys():
        try:
            return_dict[key] = dictionary[key] / total * 100
        except ZeroDivisionError:
            return_dict[key] = 0

    return return_dict


def _subtract_part_dictionary(
    total: Dict[T, N], part_dictionary: Dict[T, N]
) -> Dict[T, N]:
    return {key: total[key] - part_dictionary[key] for key in part_dictionary.keys()}


def _get_potentially_switched_candidates(
    main_unit: ReportingUnitInfo,
    reporting_unit: ReportingUnitInfo,
    amount_of_reporting_units: int,
    minimum_reporting_units: int,
    minimum_deviation_factor: int,
    minimum_votes: int,
) -> List[SwitchedCandidate]:
    # Not enough reporting units to do a good check
    if amount_of_reporting_units < minimum_reporting_units:
        return []

    received_votes = reporting_unit.votes_per_candidate
    expected_votes = _get_expected_candidate_votes(main_unit, reporting_unit)

    cands_with_more_votes: List[CandidateIdentifier] = []
    cands_with_less_votes: List[CandidateIdentifier] = []

    for cand_id in received_votes.keys():
        if received_votes[cand_id] >= minimum_votes and (
            (
                expected_votes[cand_id] == 0
                or received_votes[cand_id] / expected_votes[cand_id]
                >= minimum_deviation_factor
            )
        ):
            cands_with_more_votes.append(cand_id)
        elif (
            expected_votes[cand_id] >= minimum_votes
            and received_votes[cand_id] / expected_votes[cand_id]
            <= 1 / minimum_deviation_factor
        ):
            cands_with_less_votes.append(cand_id)

    result: List[SwitchedCandidate] = []

    for cand_with_more, cand_with_less in cartesian_product(
        cands_with_more_votes, cands_with_less_votes
    ):
        if cand_with_more.party == cand_with_less.party:
            result.append(
                SwitchedCandidate(
                    candidate_with_fewer=cand_with_less,
                    candidate_with_fewer_received=received_votes[cand_with_less],
                    candidate_with_fewer_expected=round(expected_votes[cand_with_less]),
                    candidate_with_more=cand_with_more,
                    candidate_with_more_received=received_votes[cand_with_more],
                    candidate_with_more_expected=round(expected_votes[cand_with_more]),
                )
            )

    return result


def _get_expected_candidate_votes(
    main_unit: ReportingUnitInfo, reporting_unit: ReportingUnitInfo
) -> Dict[CandidateIdentifier, float]:
    party_votes_without_current = _subtract_part_dictionary(
        main_unit.votes_per_party, reporting_unit.votes_per_party
    )
    cand_votes_without_current = _subtract_part_dictionary(
        main_unit.votes_per_candidate, reporting_unit.votes_per_candidate
    )
    cand_ratios = _get_candidate_ratios(
        party_votes_without_current, cand_votes_without_current
    )

    return {
        cand_id: ratio * reporting_unit.votes_per_party[cand_id.party]
        for cand_id, ratio in cand_ratios.items()
    }


def _get_candidate_ratios(
    party_votes: Dict[PartyIdentifier, int],
    candidate_votes: Dict[CandidateIdentifier, int],
) -> Dict[CandidateIdentifier, float]:
    return {
        cand_id: votes / party_votes[cand_id.party] if votes > 0 else 0
        for cand_id, votes in candidate_votes.items()
    }


def _get_switched_candidate_combination(
    municipality_switched: List[SwitchedCandidate],
    neighbourhood_switched: Optional[List[SwitchedCandidate]],
) -> List[SwitchedCandidate]:
    # If there are no neighbourhood results (i.e. the neighbourhood check did not run)
    # then we just return the municipality results
    if neighbourhood_switched is None:
        return municipality_switched

    # Otherwise, we only return those for which there was a neighbourhood result
    # Construct lookup tables
    municpality_lookup = {
        (cand.candidate_with_fewer, cand.candidate_with_more): cand
        for cand in municipality_switched
    }
    neighbourhood_lookup = {
        (cand.candidate_with_fewer, cand.candidate_with_more): cand
        for cand in neighbourhood_switched
    }

    # For each switch which occurs *at least* at neighbourhood level, check if it also
    # occurs at municipality level. If so, return those expected values, otherwise we
    # return the neighbourhood values
    result: List[SwitchedCandidate] = []

    for cand_id, neighbourhood_switched_obj in neighbourhood_lookup.items():
        municipality_switched_obj = municpality_lookup.get(cand_id)
        if municipality_switched_obj is not None:
            result.append(municipality_switched_obj)
        else:
            result.append(neighbourhood_switched_obj)

    return result
