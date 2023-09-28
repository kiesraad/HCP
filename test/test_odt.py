from odt import ODT, PollingStation
import pytest

expected_polling_stations_3ru = [
    PollingStation(id=1, name="Hoornes West", zip="(postcode: 2221 LA)"),
    PollingStation(id=2, name="Hoge Mors", zip="(postcode: 2222 LB)"),
    PollingStation(id=3, name="Valkenburg", zip="(postcode: 2222 LC)"),
]

expected_polling_stations_3ru_1_3_zipless = [
    PollingStation(id=1, name="Hoornes West", zip=None),
    PollingStation(id=2, name="Hoge Mors", zip="(postcode: 2222 LB)"),
    PollingStation(id=3, name="Valkenburg", zip=None),
]

test_cases_3ru = [
    ("./test/data/odts/3ru/Model_Na31-1.odt", expected_polling_stations_3ru),
    ("./test/data/odts/3ru/Model_Na31-2.odt", expected_polling_stations_3ru),
    ("./test/data/odts/3ru_spread/Model_Na31-1.odt", expected_polling_stations_3ru),
    (
        "./test/data/odts/3ru_zipless/Model_Na31-1.odt",
        expected_polling_stations_3ru_1_3_zipless,
    ),
    (
        "./test/data/odts/3ru_zipless/Model_Na31-2.odt",
        expected_polling_stations_3ru_1_3_zipless,
    ),
]

test_cases_invalid = [
    "./test/data/odts/THIS_FILE_DOES_NOT_EXIST.odt",
    "./test/data/odts/THIS_FOLDER_DOES_NOT_EXIST/Model_Na31-1.odt",
    "./test/data/odts/THIS_FOLDER_DOES_NOT_EXIST/Model_Na31-2.odt",
]


@pytest.mark.parametrize("odt_path, expected", test_cases_3ru)
def test_na31_3ru(odt_path, expected) -> None:
    odt_object = ODT.from_path(odt_path)
    assert odt_object is not None

    recounted = odt_object.get_already_recounted_polling_stations()
    assert len(recounted) == 3
    assert len(set(recounted)) == 3

    for polling_station in recounted:
        assert polling_station in expected


@pytest.mark.parametrize("odt_path", test_cases_invalid)
def test_odt_invalid(odt_path):
    odt_object = ODT.from_path(odt_path)
    assert odt_object is None
