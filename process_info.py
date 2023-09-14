## TODO mainly old code, should probably be rewritten but works in combination with the
## current EML class

percentage_blanco = 3
percentage_not_counted = 3


def differences_per_party(total_votes, reporting_units):
    difference = {}

    for key in reporting_units.keys():
        difference[key] = process_afwijking(total_votes, reporting_units[key])

    return difference


def process_afwijking(total_votes, reporting_unit):
    global_total = total_votes["total_counted"] - reporting_unit["total_counted"]
    global_party = subtract_part_dictionary(
        total_votes.get("votes_per_party"), reporting_unit.get("votes_per_party")
    )
    global_percentages = get_percentages(global_party, global_total)
    local_percentages = get_percentages(
        reporting_unit["votes_per_party"], reporting_unit["total_counted"]
    )
    difference = subtract_part_dictionary(local_percentages, global_percentages)

    return difference


def get_percentages(dictionary, total):
    return_dict = {}
    for key in dictionary.keys():
        try:
            return_dict[key] = dictionary[key] / int(total) * 100
        except ZeroDivisionError:
            return_dict[key] = 0

    return return_dict


def subtract_part_dictionary(total, part_dictionary):
    return_dict = {}
    for key in part_dictionary.keys():
        return_dict[key] = total[key] - part_dictionary[key]
    return return_dict


def get_checks_array(reporting_units_info, afwijkening):
    processed_info = {}
    for key in reporting_units_info.keys():
        processed_info[key] = create_info(reporting_units_info[key])
        processed_info[key][3] = partij_afwijking_check(afwijkening[key])

    return processed_info


def partij_afwijking_check(info_dict):
    parties_with_large_difference = []
    for key in info_dict.keys():
        if info_dict[key] > 50 or info_dict[key] < -50:
            parties_with_large_difference.append(key)
    return parties_with_large_difference or False


def create_info(reporting_unit):
    result = [False] * 4
    total = reporting_unit.get("total_counted")
    blanco = reporting_unit.get("rejected_votes").get("blanco")
    not_counted = reporting_unit.get("rejected_votes").get("ongeldig")
    if total == 0:
        result[0] = True
    result[1] = is_larger_than_percentage(total, not_counted, percentage_not_counted)
    result[2] = is_larger_than_percentage(total, blanco, percentage_blanco)

    return result


def is_larger_than_percentage(total, part, percentage):
    try:
        return int(part) / int(total) * 100 >= percentage
    except ZeroDivisionError:
        return False
