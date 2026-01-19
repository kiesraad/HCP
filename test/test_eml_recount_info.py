import pytest

from hcp.eml import EML

test_cases = [
    ("./test/data/emls/recounted_info_eml/not_recounted_cso.eml.xml", False),
    ("./test/data/emls/recounted_info_eml/recounted_cso.eml.xml", True),
    ("./test/data/emls/recounted_info_eml/not_recounted_dso.eml.xml", False),
    ("./test/data/emls/recounted_info_eml/recounted_dso.eml.xml", True),
]


@pytest.mark.parametrize("eml_path, expected_recounted_result", test_cases)
def test_eml_recounted_parsing(eml_path: str, expected_recounted_result: bool) -> None:
    parsed_eml = EML.from_xml(eml_path)
    # Each test case has exactly one reporting unit, so we can get it by index
    assert (
        expected_recounted_result
        == [value for value in parsed_eml.reporting_units_info.values()][
            0
        ].has_recounted
    )
