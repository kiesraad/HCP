import os

from main import create_csv_files


def test_create_csv_files_a_b():
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

    # No result since it has been recounted
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
            "Verkiezingnummer;Kieskringnummer;Gemeentenummer;Gemeentenaam;Stembureaunummer;Stembureaunaam;Aantal geen verklaring voor verschil;Aantal ontbrekende verklaringen voor verschil;Al herteld;Samenvatting\n"
        )
        assert content == expected

    # Result since we show this even if there has been a recount
    with open(temp_out_b) as file:
        # We skip the first few lines since the version can and will change
        content = "".join(file.readlines()[3:])
        expected = (
            "EML datum/tijd;2023-08-28T13:53:27.193\n"
            "Verkiezing;Tweede Kamer der Staten-Generaal 2023\n"
            "Datum;2023-11-22\n"
            "Kieskringnummer;14\n"
            "Gemeentenummer;0505\n"
            "\n"
            "Verkiezingnummer;Kieskringnummer;Gemeentenummer;Gemeentenaam;Stembureaunummer;Stembureaunaam;Stembureau met nul stemmen;Stembureau >=3.0% ongeldig;Stembureau >=3.0% blanco;Stembureau >=15 of >=2.0% verschil tussen toegelaten kiezers en uitgebrachte stemmen;Stembureau met lijst >=50.0% afwijking;Mogelijk verwisselde kandidaten;Al herteld;Samenvatting\n"
            "TK2023;14;0505;Dordrecht;1;Stembureau Binnenstad;;;;ja (28);;;ja;Er is een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen (28). Er is wel herteld.\n"
        )
        assert content == expected

    for temp_file in [temp_out_a, temp_out_b, temp_out_c]:
        os.remove(temp_file)


def test_create_csv_files_a_b_2():
    """Tests the controlprotocol from front to back, including reading all files from disk and writing result files.

    This test case is slightly more involved and tries to trigger each warning at least once,
    except for the switched candidates.
    """
    path_to_eml = "./test/data/e2e/Telling_EP2024_gemeente_Steenwijkerland.eml.xml"

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
            "EML datum/tijd;2024-03-13T12:37:25.756\n"
            "Verkiezing;Europees Parlement 2024\n"
            "Datum;2024-06-06\n"
            "Kieskringnummer;alle\n"
            "Gemeentenummer;1708\n"
            "\n"
            "Verkiezingnummer;Kieskringnummer;Gemeentenummer;Gemeentenaam;Stembureaunummer;Stembureaunaam;Aantal geen verklaring voor verschil;Aantal ontbrekende verklaringen voor verschil;Al herteld;Samenvatting\n"
            "EP2024;alle;1708;Steenwijkerland;1;Stembureau Holterberg;1;405;;Er is een onverklaard verschil van 1. Daarnaast is er een aantal ontbrekende verklaringen van 405. Er is niet herteld.\n"
            'EP2024;alle;1708;Steenwijkerland;3;"Stembureau ""De Waarschuwing""";108;;;Er is een onverklaard verschil van 108. Er is niet herteld.\n'
        )
        assert content == expected

    with open(temp_out_b) as file:
        # We skip the first few lines since the version can and will change
        content = "".join(file.readlines()[3:])
        expected = (
            "EML datum/tijd;2024-03-13T12:37:25.756\n"
            "Verkiezing;Europees Parlement 2024\n"
            "Datum;2024-06-06\n"
            "Kieskringnummer;alle\n"
            "Gemeentenummer;1708\n"
            "\n"
            "Verkiezingnummer;Kieskringnummer;Gemeentenummer;Gemeentenaam;Stembureaunummer;Stembureaunaam;Stembureau met nul stemmen;Stembureau >=3.0% ongeldig;Stembureau >=3.0% blanco;Stembureau >=15 of >=2.0% verschil tussen toegelaten kiezers en uitgebrachte stemmen;Stembureau met lijst >=50.0% afwijking;Mogelijk verwisselde kandidaten;Al herteld;Samenvatting\n"
            "EP2024;alle;1708;Steenwijkerland;1;Stembureau Holterberg;;;;ja (417);Kleurenpartij (51.7%);;;Er is een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen (417). Daarnaast is er een opmerkelijk grote afwijking ten opzichte van het gemeentegemiddelde bij de volgende partijen: Kleurenpartij (51.7%). Er is niet herteld.\n"
            "EP2024;alle;1708;Steenwijkerland;2;Stembureau Lege boel;ja;;;;Kleurenpartij (-51.7%);;;Er is een aantal uitgebrachte stemmen van 0. Daarnaast is er een opmerkelijk grote afwijking ten opzichte van het gemeentegemiddelde bij de volgende partijen: Kleurenpartij (-51.7%). Er is niet herteld.\n"
            'EP2024;alle;1708;Steenwijkerland;3;"Stembureau ""De Waarschuwing""";;ja (3.7%);ja (3.7%);ja (108);;;;Er is een hoog percentage ongeldige stemmen (3.7%). Daarnaast is er een hoog percentage blanco stemmen (3.7%). Ook is er een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen (108). Er is niet herteld.\n'
            "EP2024;alle;1708;Steenwijkerland;4;Stembureau Schoolstraat;;;;ja (20.0%);Het Verschil (61.7%), Kleurenpartij (-51.7%);;;Er is een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen (20.0%). Daarnaast is er een opmerkelijk grote afwijking ten opzichte van het gemeentegemiddelde bij de volgende partijen: Het Verschil (61.7%), Kleurenpartij (-51.7%). Er is niet herteld.\n"
        )
        assert content == expected

    for temp_file in [temp_out_a, temp_out_b, temp_out_c]:
        os.remove(temp_file)
