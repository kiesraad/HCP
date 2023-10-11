from eml import EML
from eml_types import (
    ReportingUnitInfo,
    EmlMetadata,
    PartyIdentifier,
    InvalidEmlException,
)
import pytest

test_eml_paths = [
    "./test/data/TK2023_DORDRECHT/Telling_TK2023_gemeente_Dordrecht.eml.xml",
    "./test/data/emls/empty_party_name.eml.xml",
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
    ),
    EML(
        eml_file_id="510b",
        main_unit_info=ReportingUnitInfo(
            reporting_unit_id=None,
            reporting_unit_name=None,
            cast=175000,
            total_counted=91250,
            rejected_votes={"ongeldig": 47, "blanco": 23},
            uncounted_votes={
                "geldige stempassen": 91190,
                "geldige volmachtbewijzen": 38,
                "geldige kiezerspassen": 32,
                "toegelaten kiezers": 91260,
                "meer getelde stembiljetten": 160,
                "minder getelde stembiljetten": 100,
                "meegenomen stembiljetten": 80,
                "te weinig uitgereikte stembiljetten": 10,
                "te veel uitgereikte stembiljetten": 95,
                "geen verklaring": 4,
                "andere verklaring": 71,
            },
            votes_per_party={
                PartyIdentifier(1, "Het Verschil"): 27750,
                PartyIdentifier(2, "Kleurenpartij"): 27500,
                PartyIdentifier(3, "Prozen en Poëzie"): 7500,
                PartyIdentifier(4, "Sportpartij"): 10500,
                PartyIdentifier(5, None): 18000,
            },
        ),
        reporting_units_info={
            "0518::SB1": ReportingUnitInfo(
                reporting_unit_id="0518::SB1",
                reporting_unit_name="Stembureau Segbroek (postcode: 2555 DA)",
                cast=90000,
                total_counted=36500,
                rejected_votes={
                    "ongeldig": 38,
                    "blanco": 22,
                },
                uncounted_votes={
                    "geldige stempassen": 36620,
                    "geldige volmachtbewijzen": 18,
                    "geldige kiezerspassen": 22,
                    "toegelaten kiezers": 36660,
                    "meer getelde stembiljetten": 0,
                    "minder getelde stembiljetten": 100,
                    "meegenomen stembiljetten": 80,
                    "te weinig uitgereikte stembiljetten": 10,
                    "te veel uitgereikte stembiljetten": 0,
                    "geen verklaring": 4,
                    "andere verklaring": 6,
                },
                votes_per_party={
                    PartyIdentifier(1, "Het Verschil"): 11100,
                    PartyIdentifier(2, "Kleurenpartij"): 11000,
                    PartyIdentifier(3, "Prozen en Poëzie"): 3000,
                    PartyIdentifier(4, "Sportpartij"): 4200,
                    PartyIdentifier(5, None): 7200,
                },
            ),
            "0518::SB2": ReportingUnitInfo(
                reporting_unit_id="0518::SB2",
                reporting_unit_name="Stembureau Laakkwartier (postcode: 2555 DB)",
                cast=85000,
                total_counted=54750,
                rejected_votes={"ongeldig": 9, "blanco": 1},
                uncounted_votes={
                    "geldige stempassen": 54570,
                    "geldige volmachtbewijzen": 20,
                    "geldige kiezerspassen": 10,
                    "toegelaten kiezers": 54600,
                    "meer getelde stembiljetten": 160,
                    "minder getelde stembiljetten": 0,
                    "meegenomen stembiljetten": 0,
                    "te weinig uitgereikte stembiljetten": 0,
                    "te veel uitgereikte stembiljetten": 95,
                    "geen verklaring": 0,
                    "andere verklaring": 65,
                },
                votes_per_party={
                    PartyIdentifier(1, "Het Verschil"): 16650,
                    PartyIdentifier(2, "Kleurenpartij"): 16500,
                    PartyIdentifier(3, "Prozen en Poëzie"): 4500,
                    PartyIdentifier(4, "Sportpartij"): 6300,
                    PartyIdentifier(5, None): 10800,
                },
            ),
        },
        metadata=EmlMetadata(
            creation_date_time="2023-07-25T12:53:44.690",
            authority_id="0518",
            authority_name="'s-Gravenhage",
            election_id="TK2023",
            election_name="Tweede Kamer der Staten-Generaal 2023",
            election_domain=None,
            election_date="2023-11-22",
            contest_identifier="12",
            reporting_unit_names={
                "0518::SB1": "Stembureau Segbroek (postcode: 2555 DA)",
                "0518::SB2": "Stembureau Laakkwartier (postcode: 2555 DB)",
            },
        ),
    ),
]


@pytest.mark.parametrize("eml_path, expected_eml", zip(test_eml_paths, expected_emls))
def test_eml_parsing(eml_path: str, expected_eml: EML) -> None:
    parsed_eml = EML.from_xml(eml_path)
    assert parsed_eml == expected_eml


def test_invalid_eml_id():
    with pytest.raises(InvalidEmlException):
        EML.from_xml("./test/data/emls/invalid_eml_id.eml.xml")
