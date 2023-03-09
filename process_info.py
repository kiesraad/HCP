def create_info(reporting_unit):
    result = [False] * 3
    total = reporting_unit.get("TotalCounted")
    blanco = reporting_unit.get("blanco")
    not_counted = reporting_unit.get("ongeldig")

    if (int(blanco)*100/int(total)) >= 3:
        result[0] = True
    if (int(not_counted)*100/int(total)) >= 3:
        result[1] = True
    if total == 0:
        result[2] = True

    return result
