import csv


def write_csv(raw_info, processed_info, meta_data):
    with open('names.csv', 'w', newline='') as csvfile:
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
        writer.writerow(['stembureau', 'nr stembureau', 'stembureau met nul stemmen', 'stembureau >3% ongeldig',
                         'stembureau >3 % blanco', 'stembureau met lijst > 50% afwijjking'])
        for key in processed_info.keys():
            info = processed_info.get(key)
            print(info)
            writer.writerow([raw_info[key]["name"], key.split("::SB")[1], info[0], info[1], info[2], info[3]])
