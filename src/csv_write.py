import csv
from eml_types import (
    EmlMetadata,
    VoteDifference,
    VoteDifferencePercentage,
    VoteDifferenceAmount,
)
from eml import CheckResult, EML
from typing import List, Dict, Optional

HEADER_COLS = [
    "Kieskringnummer",
    "Gemeentenummer",
    "Gemeentenaam",
    "Stembureaunummer",
    "Stembureaunaam",
]
PROTOCOL_VERSION = "TK2023"


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
    return f"ja ({int(percentage)}%)" if percentage else None


def _format_vote_difference(vote_difference: Optional[VoteDifference]) -> Optional[str]:
    if isinstance(vote_difference, VoteDifferenceAmount):
        part = str(vote_difference.value)
    elif isinstance(vote_difference, VoteDifferencePercentage):
        part = f"{int(vote_difference.value)}%"
    else:
        return None

    return f"ja ({part})"


def _format_percentage_deviation(percentage: float) -> str:
    percentage_int = int(percentage)
    sign = "+" if percentage_int > 0 else ""
    return f"{sign}{percentage_int}%"


def _id_cols(metadata: EmlMetadata, id: str) -> List[Optional[str]]:
    return [
        metadata.contest_identifier,
        metadata.authority_id,
        metadata.authority_name,
        _format_id(id),
        metadata.reporting_unit_names.get(id),
    ]


def write_csv_a(
    check_results: Dict[str, CheckResult], eml_metadata: EmlMetadata, csv_destination
) -> None:
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        _write_header(
            writer, eml_metadata, "Stembureaus met geen verklaring voor telverschillen"
        )

        writer.writerow(
            HEADER_COLS
            + [
                "Aantal geen verklaring voor verschil",
                "Aantal ontbrekende verklaringen voor verschil",
                "Al hergeteld",
            ]
        )

        for id, results in check_results.items():
            inexplicable_difference = results.inexplicable_difference or None
            explanation_sum_difference = results.explanation_sum_difference or None
            already_recounted = "ja" if results.already_recounted else None

            if inexplicable_difference or explanation_sum_difference:
                writer.writerow(
                    _id_cols(eml_metadata, id)
                    + [
                        inexplicable_difference,
                        explanation_sum_difference,
                        already_recounted,
                    ]
                )


def write_csv_b(
    check_results: Dict[str, CheckResult], eml_metadata: EmlMetadata, csv_destination
) -> None:
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        _write_header(
            writer,
            eml_metadata,
            f"Spreadsheet afwijkende percentages blanco en ongeldige stemmen, stembureaus met nul stemmen en afwijkingen van het lijstgemiddelde >={int(EML.PARTY_DIFFERENCE_THRESHOLD_PCT)}%",
        )

        writer.writerow(
            HEADER_COLS
            + [
                "Stembureau met nul stemmen",
                f"Stembureau >={int(EML.INVALID_VOTE_THRESHOLD_PCT)}% ongeldig",
                f"Stembureau >={int(EML.BLANK_VOTE_THRESHOLD_PCT)}% blanco",
                f"Stembureau >={EML.DIFF_VOTE_THRESHOLD} of >={int(EML.DIFF_VOTE_THRESHOLD_PCT)}% verklaarde verschillen",
                f"Stembureau met lijst >={int(EML.PARTY_DIFFERENCE_THRESHOLD_PCT)}% afwijking",
                "Al hergeteld",
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

            already_recounted = "ja" if results.already_recounted else None

            if (
                zero_votes
                or high_invalid_vote_percentage
                or high_blank_vote_percentage
                or high_explained_difference_percentage
                or parties_with_high_difference_percentage
            ):
                writer.writerow(
                    _id_cols(eml_metadata, id)
                    + [
                        zero_votes,
                        high_invalid_vote_percentage,
                        high_blank_vote_percentage,
                        high_explained_difference_percentage,
                        parties_with_high_difference_percentage,
                        already_recounted,
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

            writer.writerow(_id_cols(eml_metadata, id) + towrite)
