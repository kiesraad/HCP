import csv


def write_csv_a(check_results, csv_destination):
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["Versie controleprotocol", "VERSION_NO"])
        writer.writerow(
            ["Beschrijving", "Stembureaus met geen verklaring voor telverschillen"]
        )

        writer.writerow([])
        writer.writerow(["EML datum/tijd", "TODO"])
        writer.writerow(["Verkiezing", "TODO"])
        writer.writerow(["Datum", "TODO"])
        writer.writerow(["Gebied", "TODO"])
        writer.writerow(["Gemeentenummer", "TODO"])
        writer.writerow([])

        writer.writerow(
            [
                "Gemeentenummer",
                "Naam",
                "Stembureaunummer",
                "Stembureaunaam",
                "Aantal geen verklaring",
            ]
        )

        for id, results in check_results.items():
            inexplicable_difference = results.get("inexplicable_difference")
            if inexplicable_difference:
                writer.writerow(["TODO", "TODO", id, "TODO", inexplicable_difference])


def write_csv_b(check_results, csv_destination):
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["Versie controleprotocol", "VERSION_NO"])
        writer.writerow(
            [
                "Beschrijving",
                "Spreadsheet afwijkende percentages blanco en ongeldige stemmen, stembureaus met nul stemmen en afwijkingen van het lijstgemiddelde > 50%",
            ]
        )

        writer.writerow([])
        writer.writerow(["EML datum/tijd", "TODO"])
        writer.writerow(["Verkiezing", "TODO"])
        writer.writerow(["Datum", "TODO"])
        writer.writerow(["Gebied", "TODO"])
        writer.writerow(["Gemeentenummer", "TODO"])
        writer.writerow([])

        writer.writerow(
            [
                "Gemeentenummer",
                "Naam",
                "Stembureaunummer",
                "Stembureaunaam",
                "Stembureau met nul stemmen",
                "Stembureau >=3% ongeldig",
                "Stembureau >=3% blanco",
                "Stembureau >=2% verklaarde verschillen",
                "Stembureau met lijst >50% afwijking",
            ]
        )

        for id, results in check_results.items():
            zero_votes = "x of ja" if results.get("zero_votes") else ""
            high_invalid_vote_percentage = (
                "x of ja" if results.get("high_invalid_vote_percentage") else ""
            )
            high_blank_vote_percentage = (
                "x of ja" if results.get("high_blank_vote_percentage") else ""
            )
            high_explained_difference_percentage = (
                "x of ja" if results.get("high_explained_difference_percentage") else ""
            )
            parties_with_high_difference_percentage = ", ".join(
                results.get("parties_with_high_difference_percentage")
            )

            if (
                zero_votes
                or high_invalid_vote_percentage
                or high_blank_vote_percentage
                or high_explained_difference_percentage
                or parties_with_high_difference_percentage
            ):
                writer.writerow(
                    [
                        "TODO",
                        "TODO",
                        id,
                        "TODO",
                        zero_votes,
                        high_invalid_vote_percentage,
                        high_blank_vote_percentage,
                        high_explained_difference_percentage,
                        parties_with_high_difference_percentage,
                    ]
                )


def write_csv_c(check_results, csv_destination):
    with open(csv_destination, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["Versie controleprotocol", "VERSION_NO"])
        writer.writerow(
            [
                "Beschrijving",
                "Afwijking per stembureau per partij",
            ]
        )

        writer.writerow([])
        writer.writerow(["EML datum/tijd", "TODO"])
        writer.writerow(["Verkiezing", "TODO"])
        writer.writerow(["Datum", "TODO"])
        writer.writerow(["Gebied", "TODO"])
        writer.writerow(["Gemeentenummer", "TODO"])
        writer.writerow([])

        header = ["Stembureaunummer", "Stembureaunaam"]

        # Assuming all parties are the same
        parties = sorted(
            list(
                next(iter(check_results.values()))
                .get("party_difference_percentages")
                .keys()
            )
        )
        header += parties
        writer.writerow(header)

        for id, results in check_results.items():
            towrite = []
            differences = sorted(results.get("party_difference_percentages").items())
            for _, difference in differences:
                towrite.append(f"{int(difference)}%")

            writer.writerow([id, "TODO"] + towrite)
