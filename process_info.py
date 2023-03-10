def create_info(reporting_unit):
    result = [False] * 4
    total = reporting_unit.get("TotalCounted")
    blanco = reporting_unit.get("blanco")
    not_counted = reporting_unit.get("ongeldig")
    if total == 0:
        result[0] = True
    result[1] = is_larger_than_3_percentage(total, not_counted)
    result[2] = is_larger_than_3_percentage(total, blanco)

    return result


def is_larger_than_3_percentage(total, part):
    return int(part)/int(total)*100 >= 3
