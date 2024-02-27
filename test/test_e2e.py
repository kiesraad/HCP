import os

from main import create_csv_files


def test_create_csv_files_a():
    """Tests the controlprotocol from front to back, including reading all files from disk and writing result files.

    This test case only includes one polling station with two inexplicable differences, which does show up in the .odt
    """
    path_to_eml = (
        "./test/data/TK2023_DORDRECHT/Telling_TK2023_gemeente_Dordrecht.eml.xml"
    )
    path_to_odt = "./test/data/TK2023_DORDRECHT/Model_Na31-1.odt"

    temp_out_a = "./test/data/a.csv"
    temp_out_b = "./test/data/b.csv"
    temp_out_c = "./test/data/c.csv"

    create_csv_files(
        path_to_eml,
        temp_out_a,
        temp_out_b,
        temp_out_c,
        path_to_odt,
    )

    with open(temp_out_a) as file:
        # We skip the first few lines since the version can and will change
        content = "".join(file.readlines()[3:])
        expected = (
            "EML datum/tijd;2023-08-28T13:53:27.193\n"
            "Verkiezing;Tweede Kamer der Staten-Generaal 2023\n"
            "Datum;2023-11-22\n"
            "Kieskringnummer;14\n"
            "Gemeentenummer;0505\n"
            "\n"
            "Kieskringnummer;Gemeentenummer;Gemeentenaam;Stembureaunummer;Stembureaunaam;Aantal geen verklaring voor verschil;Aantal ontbrekende verklaringen voor verschil;Al hergeteld\n"
            "14;0505;Dordrecht;1;Stembureau Binnenstad (postcode: 3331 DA);2;;ja\n"
        )
        assert content == expected

    for temp_file in [temp_out_a, temp_out_b, temp_out_c]:
        os.remove(temp_file)
