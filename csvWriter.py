import csv


def write_csv(raw_info, processed_info, meta_data, afwijkeningen):
    with open(meta_data.get("gebied")+"-"+meta_data.get("date")+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["sep=,"])
        writer.writerow(["Versie controleprotocol"])
        writer.writerow(["Beschrijving", "spreadsheet afwijkende percentages blanco en ongeldige stemmen, "
                                         "stembureaus met nul stemmen en afwijkingen van het lijstgemiddelde > 50%"])
        writer.writerow([""])
        writer.writerow(["EML datum/tijd", meta_data["eml_date"]])
        writer.writerow(["Verkiezing", meta_data["name"]])
        writer.writerow(["Datum", meta_data["date"]])
        writer.writerow(["Gebied", meta_data["gebied"]])
        writer.writerow(["Nummer", meta_data["id"]])

        writer.writerow([""])
        arr = ['stembureau', 'nr stembureau', 'stembureau met nul stemmen', 'stembureau >3% ongeldig',
                         'stembureau >3 % blanco', 'stembureau met lijst > 50% afwijking', "afwijking per partij:"]
        for key in afwijkeningen.keys():
            for key2 in afwijkeningen[key].keys():
                arr.append(key2)
            break
        writer.writerow(arr)
        for key in processed_info.keys():
            if check_any_true(processed_info[key]):
                result_row = create_result_row(raw_info[key], processed_info[key], key.split("::SB")[1], afwijkeningen[key])
                writer.writerow(result_row)


def create_result_row(raw_info, info, nr, afwijkeningen):
    write_row = [""]*(7 + len(afwijkeningen))
    write_row[0] = raw_info["name"]
    write_row[1] = nr
    if info[0]:
        write_row[2] = "x of ja"
    if info[1]:
        write_row[3] = "x of ja"
    if info[2]:
        write_row[4] = "x of ja"
    if info[3]:
        write_row[5] = info[3]

    write_row[6] = ""
    for idx, key in enumerate(afwijkeningen.keys()):
        write_row[7+idx] = str(int(afwijkeningen[key]))+"%"

    return write_row


def check_any_true(info):
    for i in info:
        if i:
            return True
    return False
