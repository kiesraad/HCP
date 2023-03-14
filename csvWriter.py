import csv


def write_csv(raw_info, processed_info, meta_data):
    with open(meta_data.get("gebied")+"-"+meta_data.get("date")+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["sep=,"])
        writer.writerow(["Versie controleprotocol"])
        writer.writerow(["Beschrijving", "afwijking per stembureau per partij"])
        writer.writerow([""])
        writer.writerow(["EML datum/tijd", meta_data["eml_date"]])
        writer.writerow(["Verkiezing", meta_data["name"]])
        writer.writerow(["Datum", meta_data["date"]])
        writer.writerow(["Gebied", meta_data["gebied"]])
        writer.writerow(["Nummer", meta_data["id"]])

        writer.writerow([""])
        arr = ['stembureau', 'nr stembureau', 'stembureau met nul stemmen', 'stembureau >3% ongeldig',
                'stembureau >3 % blanco', 'stembureau met lijst > 50% afwijking']

        writer.writerow(arr)
        for key in processed_info.keys():
            if check_any_true(processed_info[key]):
                result_row = create_result_row(raw_info[key], processed_info[key], key.split("::SB")[1])
                writer.writerow(result_row)


def write_afwijkeningen(meta_data, afwijkingen, raw_info):
    with open(meta_data.get("gebied")+"-"+meta_data.get("date")+'-afwijkingen.csv', 'w', newline='') as csvfile:
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
        arr = ["naam"]
        for key in afwijkingen.keys():
            for key2 in afwijkingen[key].keys():
                arr.append(key2)
            break
        writer.writerow(arr)

        for key in afwijkingen.keys():
            arr = [raw_info[key]["name"]]
            for key2 in afwijkingen[key].keys():
                arr.append(str(int(afwijkingen[key][key2]))+"%")
            writer.writerow(arr)

def create_result_row(raw_info, info, nr):
    write_row = [""]*6
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

    return write_row


def create_afwijking_row(afwijking):
    return_arr = []
    for idx, key in enumerate(afwijking.keys()):
        return_arr[idx] = str(int(afwijking[key]))+"%"
    return return_arr


def check_any_true(info):
    for i in info:
        if i:
            return True
    return False
