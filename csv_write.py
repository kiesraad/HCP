import csv
from eml_types import EmlMetadata
from eml import CheckResult
from typing import List, Union, Dict

HEADER_COLS = [
    "Kieskringnummer",
    "Gemeentenummer",
    "Gemeentenaam",
    "Stembureaunummer",
    "Stembureaunaam",
]


def _write_header(writer, metadata: EmlMetadata, description: str) -> None:
    writer.writerow(["Versie controleprotocol", "VERSION_NO"])
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


def _id_cols(metadata: EmlMetadata, id: str) -> List[Union[str, None]]:
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

        writer.writerow(HEADER_COLS + ["Aantal geen verklaring", "Al hergeteld"])

        for id, results in check_results.items():
            inexplicable_difference = results.inexplicable_difference
            already_recounted = "x of ja" if results.already_recounted else None
            if inexplicable_difference:
                writer.writerow(
                    _id_cols(eml_metadata, id)
                    + [inexplicable_difference, already_recounted]
                )


def write_csv_b(
    check_results: Dict[str, CheckResult], eml_metadata: EmlMetadata, csv_destination
) -> None:
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        _write_header(
            writer,
            eml_metadata,
            "Spreadsheet afwijkende percentages blanco en ongeldige stemmen, stembureaus met nul stemmen en afwijkingen van het lijstgemiddelde > 50%",
        )

        writer.writerow(
            HEADER_COLS
            + [
                "Stembureau met nul stemmen",
                "Stembureau >=3% ongeldig",
                "Stembureau >=3% blanco",
                "Stembureau >=2% verklaarde verschillen",
                "Stembureau met lijst >=50% afwijking",
            ]
        )

        for id, results in check_results.items():
            zero_votes = "x of ja" if results.zero_votes else ""
            high_invalid_vote_percentage = (
                "x of ja" if results.high_invalid_vote_percentage else ""
            )
            high_blank_vote_percentage = (
                "x of ja" if results.high_blank_vote_percentage else ""
            )
            high_explained_difference_percentage = (
                "x of ja" if results.high_explained_difference_percentage else ""
            )
            parties_with_high_difference_percentage = ", ".join(
                results.parties_with_high_difference_percentage
            )

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
                    ]
                )


def write_csv_c(
    check_results: Dict[str, CheckResult], eml_metadata: EmlMetadata, csv_destination
) -> None:
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        _write_header(writer, eml_metadata, "Afwijking per stembureau per partij")

        # Assuming all parties are the same
        parties = sorted(
            list(next(iter(check_results.values())).party_difference_percentages.keys())
        )
        writer.writerow(HEADER_COLS + parties)

        for id, results in check_results.items():
            towrite = []
            differences = sorted(results.party_difference_percentages.items())
            for _, difference in differences:
                towrite.append(f"{int(difference)}%")

            writer.writerow(_id_cols(eml_metadata, id) + towrite)
