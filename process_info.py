from pprint import pprint

percentage_blanco = 3
percentage_not_counted = 3
percentage_afwijking = 50

pp = pprint


def process_50_afwijking(total_votes, reporting_units):
    difference = {}

    for key in reporting_units.keys():
        difference[key] = process_afwijking(total_votes, reporting_units[key])

    return difference


def process_afwijking(total_votes, reporting_unit):
    global_total = total_votes["TotalCounted"] - reporting_unit["TotalCounted"]
    global_party = subtract_dictionary(total_votes.get("party_vote_count"), reporting_unit.get("party_vote_count"))
    global_percentages = get_percentages(global_party, global_total)
    local_percentages = get_percentages(reporting_unit["party_vote_count"], reporting_unit["TotalCounted"])
    difference = subtract_dictionary(local_percentages, global_percentages)

    return difference


def get_percentages(dictionary, total):
    return_dict = {}
    for key in dictionary.keys():
        return_dict[key] = dictionary[key]/total*100

    return return_dict


def subtract_dictionary(minuend, subtrahend):
    return_dict = {}
    for key in minuend.keys():
        return_dict[key] = minuend[key] - subtrahend[key]
    return return_dict


def create_info_array(reporting_units_info, afwijkingen):
    processed_info = {}
    for key in reporting_units_info.keys():
        processed_info[key] = create_info(reporting_units_info[key])
        processed_info[key][3] = partij_afwijking_check(afwijkingen[key])

    return processed_info


def partij_afwijking_check(info_dict):
    for key in info_dict.keys():
        if info_dict[key] > percentage_afwijking or info_dict[key] < -percentage_afwijking:
            return key
    return False


def create_info(reporting_unit):
    result = [False] * 4
    total = reporting_unit.get("TotalCounted")
    not_counted = reporting_unit.get("uncounted_votes").get("ongeldig")
    blanco = reporting_unit.get("uncounted_votes").get("blanco")
    if total == 0:
        result[0] = True
    result[1] = is_larger_than_percentage(total, not_counted,  percentage_not_counted)
    result[2] = is_larger_than_percentage(total, blanco,  percentage_blanco)

    return result


def is_larger_than_percentage(total, part, percentage):
    return int(part)/int(total)*100 >= percentage
