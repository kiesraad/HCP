import zipfile, xml_parser

PERCENTAGE_REJECTED_THRESHOLDS = {"blanco": float(3), "ongeldig": float(3)}
PERCENTAGE_PARTY_DIFF_THRESHOLD = float(50)

#### Check functions


def check_zero_votes(reporting_unit) -> bool:
    return _get_total_votes(reporting_unit) == 0


def check_inexplicable_difference(reporting_unit) -> bool:
    return reporting_unit.get("uncounted_votes").get("geen verklaring") > 0


def check_too_many_rejected_votes(reporting_unit, kind: str) -> bool:
    if kind not in PERCENTAGE_REJECTED_THRESHOLDS.keys():
        raise ValueError(f"Invalid rejected vote kind passed: {kind}")

    rejected_votes = reporting_unit.get("rejected_votes").get(kind)
    threshold = PERCENTAGE_REJECTED_THRESHOLDS.get(kind)
    total_votes = _get_total_votes(reporting_unit)
    return _is_larger_than_percentage(rejected_votes, total_votes, threshold)


def get_party_difference_percentages(main_unit, reporting_unit):
    global_total = main_unit["total_counted"] - reporting_unit["total_counted"]
    global_party = _subtract_part_dictionary(
        main_unit.get("votes_per_party"), reporting_unit.get("votes_per_party")
    )
    global_percentages = _get_percentages(global_party, global_total)
    local_percentages = _get_percentages(
        reporting_unit["votes_per_party"], reporting_unit["total_counted"]
    )
    difference = _subtract_part_dictionary(local_percentages, global_percentages)

    return difference


def check_parties_with_large_percentage_difference(
    main_unit, reporting_unit
) -> list[dict]:
    differences = get_party_difference_percentages(main_unit, reporting_unit)
    return [
        {"party_name": name, "difference": difference}
        for (name, difference) in differences.items()
        if abs(difference) >= PERCENTAGE_PARTY_DIFF_THRESHOLD
    ]


def get_na31_1_recounts(odt_path):
    with zipfile.ZipFile(odt_path) as odt_zip:
        with odt_zip.open("content.xml") as odt_xml:
            odt_root = xml_parser.parse_xml(odt_xml)
            return xml_parser.get_polling_stations_with_recounts(odt_root)


#### Helper functions


def _get_total_votes(reporting_unit) -> int:
    rejected_votes = reporting_unit.get("rejected_votes")
    return (
        reporting_unit.get("total_counted")
        + rejected_votes.get("ongeldig")
        + rejected_votes.get("blanco")
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
