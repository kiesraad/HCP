from typing import List
from eml_types import ReportingUnitInfo, PartyIdentifier
from typing import Dict

# Check functions


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
) -> bool:
    if kind not in ["ongeldig", "blanco"]:
        raise ValueError(f"Invalid rejected vote kind passed: {kind}")

    rejected_votes = reporting_unit.rejected_votes.get(kind)
    total_votes = _get_total_votes(reporting_unit)
    return _is_larger_than_percentage(rejected_votes, total_votes, threshold_pct)


def check_too_many_explained_differences(
    reporting_unit: ReportingUnitInfo, threshold_pct: float
) -> bool:
    explained_differences = _get_explained_differences(reporting_unit)
    total_votes = _get_total_votes(reporting_unit)

    return _is_larger_than_percentage(explained_differences, total_votes, threshold_pct)


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
            identifier.name or f"{identifier.id}. blanco"
            for (identifier, difference) in differences.items()
            if abs(difference) >= threshold_pct
        ]
    )


# Helper functions


def _get_total_votes(reporting_unit: ReportingUnitInfo) -> int:
    rejected_votes = reporting_unit.rejected_votes
    return (
        reporting_unit.total_counted
        + rejected_votes["ongeldig"]
        + rejected_votes["blanco"]
    )


def _get_explained_differences(reporting_unit: ReportingUnitInfo) -> int:
    # Metadata fields
    uncounted_votes = reporting_unit.uncounted_votes
    return (
        (uncounted_votes.get("meegenomen stembiljetten") or 0)
        + (uncounted_votes.get("te weinig uitgereikte stembiljetten") or 0)
        + (uncounted_votes.get("te veel uitgereikte stembiljetten") or 0)
        + (uncounted_votes.get("andere verklaring") or 0)
    )


def _is_larger_than_percentage(part, total, percentage):
    try:
        return int(part) / int(total) * 100 >= percentage
    except ZeroDivisionError:
        return False


def _get_percentages(dictionary, total):
    return_dict = {}
    for key in dictionary.keys():
        try:
            return_dict[key] = dictionary[key] / int(total) * 100
        except ZeroDivisionError:
            return_dict[key] = 0

    return return_dict


def _subtract_part_dictionary(total, part_dictionary):
    return_dict = {}
    for key in part_dictionary.keys():
        return_dict[key] = total[key] - part_dictionary[key]
    return return_dict
