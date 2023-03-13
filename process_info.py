percentage_blanco = 3
percentage_not_counted = 3


def create_info(reporting_unit):
    result = [False] * 4
    total = reporting_unit.get("TotalCounted")
    blanco = reporting_unit.get("uncounted_votes").get("blanco")
    not_counted = reporting_unit.get("uncounted_votes").get("ongeldig")
    if total == 0:
        result[0] = True
    result[1] = is_larger_than_percentage(total, not_counted,  percentage_not_counted)
    result[2] = is_larger_than_percentage(total, blanco,  percentage_blanco)

    return result


def is_larger_than_percentage(total, part, percentage):
    return int(part)/int(total)*100 >= percentage
