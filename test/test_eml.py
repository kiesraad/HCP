from eml import EML
from eml_types import ReportingUnitInfo, EmlMetadata, PartyIdentifier
import pytest

test_eml_paths = [
    "./test/data/TK2023_DORDRECHT/Telling_TK2023_gemeente_Dordrecht.eml.xml"
]

expected_emls = [
    EML(
        eml_file_id="510b",
        main_unit_info=ReportingUnitInfo(
            reporting_unit_id=None,
            reporting_unit_name=None,
            cast=72100,
            total_counted=72065,
            rejected_votes={"ongeldig": 3, "blanco": 2},
            uncounted_votes={
                "geldige stempassen": 72095,
                "geldige volmachtbewijzen": 3,
                "geldige kiezerspassen": 0,
                "toegelaten kiezers": 72098,
                "meer getelde stembiljetten": 0,
                "minder getelde stembiljetten": 28,
                "meegenomen stembiljetten": 23,
                "te weinig uitgereikte stembiljetten": 3,
                "te veel uitgereikte stembiljetten": 0,
                "geen verklaring": 2,
                "andere verklaring": 0,
            },
            votes_per_party={
                PartyIdentifier(1, "Het Verschil"): 25205,
                PartyIdentifier(2, "Kleurenpartij"): 32460,
                PartyIdentifier(3, "Prozen en Poëzie"): 9000,
                PartyIdentifier(4, "Sportpartij"): 5400,
            },
        ),
        reporting_units_info={
            "0505::SB1": ReportingUnitInfo(
                reporting_unit_id="0505::SB1",
                reporting_unit_name="Stembureau Binnenstad (postcode: 3331 DA)",
                cast=72100,
                total_counted=72065,
                rejected_votes={"ongeldig": 3, "blanco": 2},
                uncounted_votes={
                    "geldige stempassen": 72095,
                    "geldige volmachtbewijzen": 3,
                    "geldige kiezerspassen": 0,
                    "toegelaten kiezers": 72098,
                    "meer getelde stembiljetten": 0,
                    "minder getelde stembiljetten": 28,
                    "meegenomen stembiljetten": 23,
                    "te weinig uitgereikte stembiljetten": 3,
                    "te veel uitgereikte stembiljetten": 0,
                    "geen verklaring": 2,
                    "andere verklaring": 0,
                },
                votes_per_party={
                    PartyIdentifier(1, "Het Verschil"): 25205,
                    PartyIdentifier(2, "Kleurenpartij"): 32460,
                    PartyIdentifier(3, "Prozen en Poëzie"): 9000,
                    PartyIdentifier(4, "Sportpartij"): 5400,
                },
            )
        },
        metadata=EmlMetadata(
            creation_date_time="2023-08-28T13:53:27.193",
            authority_id="0505",
            authority_name="Dordrecht",
            election_id="TK2023",
            election_name="Tweede Kamer der Staten-Generaal 2023",
            election_domain=None,
            election_date="2023-11-22",
            contest_identifier="14",
            reporting_unit_names={
                "0505::SB1": "Stembureau Binnenstad (postcode: 3331 DA)"
            },
        ),
    )
]


@pytest.mark.parametrize("eml_path, expected_eml", zip(test_eml_paths, expected_emls))
def test_eml_parsing(eml_path: str, expected_eml: EML) -> None:
    parsed_eml = EML.from_xml(eml_path)
    assert parsed_eml == expected_eml
