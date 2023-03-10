def create_info(reporting_unit):
    result = [False] * 4
    total = reporting_unit.get("TotalCounted")
    blanco = reporting_unit.get("blanco")
    not_counted = reporting_unit.get("ongeldig")

    result[0] = is_larger_than_3_percentage(total, blanco)
    result[1] = is_larger_than_3_percentage(total, not_counted)
    if total == 0:
        result[2] = True

    return result


def is_larger_than_3_percentage(total, part):
    return int(part)*100/int(total)
