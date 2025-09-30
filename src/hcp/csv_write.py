import csv
import re
from typing import Dict, List, Literal, Optional

from .eml import EML, CheckResult
from .eml_types import (
    EmlMetadata,
    SummaryType,
    SwitchedCandidate,
    VoteDifference,
    VoteDifferenceAmount,
    VoteDifferencePercentage,
)

HEADER_COLS = [
    "Verkiezingnummer",
    "Type",
    "Kieskringnummer",
    "Gemeentenummer",
    "Gemeentenaam",
    "Stembureaunummer",
    "Stembureaunaam",
]
PROTOCOL_VERSION = "TK2025"

ZIP_CODE_PATTERN = re.compile(r"\(\s*postcode:\s*\d{4}\s*[A-Z]{2}\s*\)")
STEMBUREAU_PREFIX_PATTERN = re.compile(r"^(Stembureau\s)+")


def _write_header(writer, metadata: EmlMetadata, description: str) -> None:
    writer.writerow(["Versie controleprotocol", PROTOCOL_VERSION])
    writer.writerow(["Beschrijving", description])

    writer.writerow([])
    writer.writerow(["EML datum/tijd", metadata.creation_date_time])
    writer.writerow(["Verkiezing", metadata.election_name])
    writer.writerow(["Datum", metadata.election_date])
    writer.writerow(["Kieskringnummer", metadata.contest_identifier])
    writer.writerow(["Gemeentenummer", metadata.authority_id])
    writer.writerow([])


def _format_id(id: str) -> str:
    return id[8:]


def _format_percentage(percentage: Optional[float]) -> Optional[str]:
    return f"ja ({round(percentage, 1)}%)" if percentage else None


def _format_vote_difference(vote_difference: Optional[VoteDifference]) -> Optional[str]:
    if isinstance(vote_difference, VoteDifferenceAmount):
        part = str(vote_difference.value)
    elif isinstance(vote_difference, VoteDifferencePercentage):
        part = f"{round(vote_difference.value, 1)}%"
    else:
        return None

    return f"ja ({part})"


def _format_potentially_switched_candidates(
    potentially_switched_candidates: List[SwitchedCandidate],
) -> Optional[str]:
    if len(potentially_switched_candidates) == 0:
        return None
    return ", ".join([str(cand) for cand in potentially_switched_candidates])


def _format_percentage_deviation(percentage: float) -> str:
    percentage_rounded = round(percentage, 1)
    sign = "+" if percentage_rounded > 0.0 else ""
    return f"{sign}{percentage_rounded}%"


def _format_reporting_unit_name(reporting_unit_name: Optional[str]) -> str:
    return (
        STEMBUREAU_PREFIX_PATTERN.sub(
            "", ZIP_CODE_PATTERN.sub("", reporting_unit_name)
        ).strip()
        if reporting_unit_name
        else ""
    )


def _id_cols(
    metadata: EmlMetadata, id: str, type: Literal["A", "B", "C"]
) -> List[Optional[str]]:
    return [
        metadata.election_id,
        type,
        metadata.contest_identifier,
        metadata.authority_id,
        metadata.authority_name,
        _format_id(id),
        _format_reporting_unit_name(metadata.reporting_unit_names.get(id)),
    ]


def write_csv_a(
    check_results: Dict[str, CheckResult],
    eml_metadata: EmlMetadata,
    odt_used: bool,
    csv_destination,
) -> None:
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        _write_header(
            writer,
            eml_metadata,
            f"Stembureaus met geen verklaring voor telverschillen (odt {("gebruikt" if odt_used else "niet gebruikt")})",
        )

        writer.writerow(
            HEADER_COLS
            + [
                "Aantal geen verklaring voor verschil",
                "Aantal ontbrekende verklaringen voor verschil",
                "Al herteld",
                "Samenvatting",
            ]
        )

        for id, results in check_results.items():
            inexplicable_difference = results.inexplicable_difference or None
            explanation_sum_difference = results.explanation_sum_difference or None
            already_recounted = "ja" if results.already_recounted else None

            if (
                inexplicable_difference or explanation_sum_difference
            ) and not results.already_recounted:
                writer.writerow(
                    _id_cols(eml_metadata, id, "A")
                    + [
                        inexplicable_difference,
                        explanation_sum_difference,
                        already_recounted,
                        results.summarise(SummaryType.A),
                    ]
                )


def write_csv_b(
    check_results: Dict[str, CheckResult],
    eml_metadata: EmlMetadata,
    neighbourhoods_used: bool,
    csv_destination,
) -> None:
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        _write_header(
            writer,
            eml_metadata,
            (
                f"Spreadsheet afwijkende percentages blanco en ongeldige stemmen, "
                "stembureaus met nul stemmen, "
                f"afwijkingen van het lijstgemiddelde >={EML.PARTY_DIFFERENCE_THRESHOLD_PCT}% "
                f"en mogelijk verwisselde kandidaten (wijkdata {"gebruikt" if neighbourhoods_used else "niet_gebruikt"})"
            ),
        )

        writer.writerow(
            HEADER_COLS
            + [
                "Stembureau met nul stemmen",
                f"Stembureau >={EML.INVALID_VOTE_THRESHOLD_PCT}% ongeldig",
                f"Stembureau >={EML.BLANK_VOTE_THRESHOLD_PCT}% blanco",
                (
                    f"Stembureau >={EML.DIFF_VOTE_THRESHOLD} of >={EML.DIFF_VOTE_THRESHOLD_PCT}% verschil "
                    "tussen toegelaten kiezers en uitgebrachte stemmen"
                ),
                f"Stembureau met lijst >={EML.PARTY_DIFFERENCE_THRESHOLD_PCT}% afwijking",
                "Mogelijk verwisselde kandidaten",
                "Al herteld",
                "Samenvatting",
            ]
        )

        for id, results in check_results.items():
            zero_votes = "ja" if results.zero_votes else None
            high_invalid_vote_percentage = _format_percentage(
                results.high_invalid_vote_percentage
            )
            high_blank_vote_percentage = _format_percentage(
                results.high_blank_vote_percentage
            )
            high_explained_difference_percentage = _format_vote_difference(
                results.high_vote_difference
            )
            parties_with_high_difference_percentage = ", ".join(
                results.parties_with_high_difference_percentage
            )
            potentially_switched_candidates = _format_potentially_switched_candidates(
                results.potentially_switched_candidates
            )
            already_recounted = "ja" if results.already_recounted else None

            if (
                zero_votes
                or high_invalid_vote_percentage
                or high_blank_vote_percentage
                or high_explained_difference_percentage
                or parties_with_high_difference_percentage
                or potentially_switched_candidates
            ):
                writer.writerow(
                    _id_cols(eml_metadata, id, "B")
                    + [
                        zero_votes,
                        high_invalid_vote_percentage,
                        high_blank_vote_percentage,
                        high_explained_difference_percentage,
                        parties_with_high_difference_percentage,
                        potentially_switched_candidates,
                        already_recounted,
                        results.summarise(SummaryType.B),
                    ]
                )


def write_csv_c(
    check_results: Dict[str, CheckResult], eml_metadata: EmlMetadata, csv_destination
) -> None:
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        _write_header(writer, eml_metadata, "Afwijking per stembureau per partij")

        # Assuming all parties are the same
        parties = [
            identifier.name
            for identifier in sorted(
                list(
                    next(
                        iter(check_results.values())
                    ).party_difference_percentages.keys()
                )
            )
        ]
        writer.writerow(HEADER_COLS + parties)

        for id, results in check_results.items():
            towrite = []
            differences = sorted(results.party_difference_percentages.items())
            for _, difference in differences:
                towrite.append(_format_percentage_deviation(difference))

            writer.writerow(_id_cols(eml_metadata, id, "C") + towrite)
