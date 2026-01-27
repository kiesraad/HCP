import os

from hcp.main import create_csv_files


def test_create_csv_files_a_b():
    """Tests the controlprotocol from front to back, including reading all files from disk and writing result files.

    This test case is slightly more involved and tries to trigger each warning at least once,
    except for the switched candidates.
    """
    path_to_eml = "./test/data/e2e/FAKE_TEST_DATA_Telling_GR2026_Juinen_DSO.eml.xml"

    temp_out_a = "./test/data/a.csv"
    temp_out_b = "./test/data/b.csv"
    temp_out_c = "./test/data/c.csv"

    create_csv_files(
        path_to_eml,
        temp_out_a,
        temp_out_b,
        temp_out_c,
    )

    # Result since we do not know if there has been a recount
    with open(temp_out_a) as file:
        # We skip the first few lines since the version can and will change
        content = "".join(file.readlines()[3:])
        expected = (
            "EML datum/tijd;2026-01-16T09:14:34.838\n"
            "Verkiezing;Gemeenteraad Juinen 2026\n"
            "Datum;2026-03-18\n"
            "Kieskringnummer;geen\n"
            "Gemeentenummer;9999\n"
            "\n"
            "Verkiezingnummer;Type;Kieskringnummer;Gemeentenummer;Gemeentenaam;Stembureaunummer;Stembureaunaam;Niet onderzocht telverschil;Al herteld;Samenvatting\n"
            "GR2026_Juinen;A;geen;9999;Juinen;1;Purmerland;545;;Er is een verschil tussen het aantal toegelaten kiezers en het aantal getelde stembiljetten van 545. Volgens het GSB is dit niet herteld of onderzocht.\n"
        )
        assert content == expected

    with open(temp_out_b) as file:
        # We skip the first few lines since the version can and will change
        content = "".join(file.readlines()[3:])
        expected = (
            "EML datum/tijd;2026-01-16T09:14:34.838\n"
            "Verkiezing;Gemeenteraad Juinen 2026\n"
            "Datum;2026-03-18\n"
            "Kieskringnummer;geen\n"
            "Gemeentenummer;9999\n"
            "\n"
            "Verkiezingnummer;Type;Kieskringnummer;Gemeentenummer;Gemeentenaam;Stembureaunummer;Stembureaunaam;Stembureau met nul stemmen;Stembureau >=3.0% ongeldig;Stembureau >=3.0% blanco;Stembureau >=15 of >=2.0% verschil tussen toegelaten kiezers en uitgebrachte stemmen;Stembureau met lijst >=60.0% afwijking;Mogelijk verwisselde kandidaten;Al herteld;Samenvatting\n"
            "GR2026_Juinen;B;geen;9999;Juinen;1;Purmerland;;ja (3.1%);ja (5.3%);ja (545);;;;Er is een hoog percentage ongeldige stemmen (3.1%). Daarnaast is er een hoog percentage blanco stemmen (5.3%). Ook is er een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen (545).\n"
            "GR2026_Juinen;B;geen;9999;Juinen;2;Grootschermer;ja;;;ja (4605);;;ja;Er is een aantal uitgebrachte stemmen van 0. Daarnaast is er een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen (4605).\n"
            "GR2026_Juinen;B;geen;9999;Juinen;3;Middenbeemster;;;;ja (1005);Het Verschil (140.6%);;ja;Er is een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen (1005). Daarnaast is er een opmerkelijk grote afwijking ten opzichte van het gemeentegemiddelde bij de volgende partijen: Het Verschil (140.6%).\n"
        )
        assert content == expected

    for temp_file in [temp_out_a, temp_out_b, temp_out_c]:
        os.remove(temp_file)
