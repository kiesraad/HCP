from defusedxml import ElementTree as ET
from typing import Optional, IO, Union, List, Dict
from xml.etree.ElementTree import Element as XmlElement
from eml_types import EmlMetadata, ReportingUnitInfo

NAMESPACE = {
    "eml": "urn:oasis:names:tc:evs:schema:eml",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "kr": "http://www.kiesraad.nl/extensions",
    "xal": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    "xnl": "urn:oasis:names:tc:ciq:xsdschema:xNL:2.0",
}


def get_text(xml_element: Optional[XmlElement]) -> Optional[str]:
    return xml_element.text if xml_element is not None else None


def get_mandatory_text(xml_element: Optional[XmlElement]) -> str:
    if xml_element is None:
        raise ValueError("Could not find specified XML element")

    text = xml_element.text
    if text is None:
        raise AttributeError(
            f"Element {xml_element} did not have text but was mandatory"
        )

    return text


def get_attrib(xml_element: Optional[XmlElement], attrib_name: str) -> Optional[str]:
    return xml_element.attrib.get(attrib_name) if xml_element is not None else None


def parse_xml(file_name: Union[str, IO[bytes]]) -> XmlElement:
    # EML should be checked so that it validates using the XSD

    tree = ET.parse(file_name)
    tree_root = tree.getroot()
    # Probably check if the root is of type EML here

    return tree_root


def get_eml_type(root: XmlElement) -> Optional[str]:
    root_element = root.find(".")
    if root_element and root_element.tag == f"{{{NAMESPACE.get('eml')}}}EML":
        return get_attrib(root_element, "Id")

    return None


def get_metadata(root: XmlElement) -> EmlMetadata:
    creation_date_time = get_text(root.find("./kr:CreationDateTime", NAMESPACE))
    authority_id = get_attrib(
        root.find(
            "./eml:ManagingAuthority/eml:AuthorityIdentifier",
            NAMESPACE,
        ),
        "Id",
    )
    authority_name = get_text(
        root.find(
            "./eml:ManagingAuthority/eml:AuthorityIdentifier",
            NAMESPACE,
        )
    )
    election_id = get_attrib(
        root.find("./eml:Count/eml:Election/eml:ElectionIdentifier", NAMESPACE), "Id"
    )
    election_name = get_text(
        root.find(
            "./eml:Count/eml:Election/eml:ElectionIdentifier/eml:ElectionName",
            NAMESPACE,
        )
    )
    election_domain = get_text(
        root.find(
            "./eml:Count/eml:Election/eml:ElectionIdentifier/kr:ElectionDomain",
            NAMESPACE,
        ),
    )
    election_date = get_text(
        root.find(
            "./eml:Count/eml:Election/eml:ElectionIdentifier/kr:ElectionDate",
            NAMESPACE,
        )
    )
    contest_identifier = get_attrib(
        root.find(
            "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:ContestIdentifier",
            NAMESPACE,
        ),
        "Id",
    )

    reporting_units = root.findall(".//eml:ReportingUnitIdentifier", NAMESPACE)
    reporting_unit_names = {
        get_attrib(elem, "Id"): get_text(elem) for elem in reporting_units
    }

    return EmlMetadata(
        creation_date_time=creation_date_time,
        authority_id=authority_id,
        authority_name=authority_name,
        election_id=election_id,
        election_name=election_name,
        election_domain=election_domain,
        election_date=election_date,
        contest_identifier=contest_identifier,
        reporting_unit_names=reporting_unit_names,
    )


def get_reporting_units(xml: XmlElement) -> List[XmlElement]:
    reporting_units = xml.findall(
        "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:ReportingUnitVotes",
        NAMESPACE,
    )

    # Probably check if the amount of reporting units > 0, otherwise the EML might have been
    # invalid, indicating a wrong structure, or the individual polling stations were not
    # included in the EML.

    return reporting_units


def get_main_unit(xml: XmlElement) -> XmlElement:
    main_unit = xml.find(
        "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:TotalVotes", NAMESPACE
    )

    if main_unit is None:
        raise AttributeError("EML had no main reporting unit!")

    return main_unit


def get_reporting_unit_info(reporting_unit: XmlElement) -> ReportingUnitInfo:
    # Reporing unit element, which is present for the individual polling stations but
    # not for the 'total' count of the GSB
    reporting_unit_id_element = reporting_unit.find(
        "./eml:ReportingUnitIdentifier", NAMESPACE
    )
    reporting_unit_id = get_attrib(reporting_unit_id_element, "Id")
    reporting_unit_name = get_text(reporting_unit_id_element)

    # Get amount of eligible voters
    cast = int(get_mandatory_text(reporting_unit.find("./eml:Cast", NAMESPACE)))

    # Get total cast/counted votes
    total_counted = int(
        get_mandatory_text(reporting_unit.find("./eml:TotalCounted", NAMESPACE))
    )

    # Fetch invalid votes, the two types are mandatory
    # which are 'blanco' (blank) and 'ongeldig' (invalid)
    rejected_votes = get_vote_metadata_dict(reporting_unit, "./eml:RejectedVotes")

    # Fetch 'uncounted votes' which is metadata about the polling station
    uncounted_votes = get_vote_metadata_dict(reporting_unit, "./eml:UncountedVotes")

    # Fetch amount of votes per party
    votes_per_party = get_votes_per_party(reporting_unit)

    return ReportingUnitInfo(
        reporting_unit_id=reporting_unit_id,
        reporting_unit_name=reporting_unit_name,
        cast=cast,
        total_counted=total_counted,
        rejected_votes=rejected_votes,
        uncounted_votes=uncounted_votes,
        votes_per_party=votes_per_party,
    )


def get_vote_metadata_dict(reporting_unit: XmlElement, path: str) -> Dict[str, int]:
    vote_metadata = reporting_unit.findall(path, NAMESPACE)
    result = {}

    for elem in vote_metadata:
        reasoncode = elem.attrib["ReasonCode"]
        value = elem.text

        if value is None:
            raise ValueError(
                f"Vote metadata {reasoncode} did not have associated value"
            )

        result[reasoncode] = int(value)

    return result


def get_votes_per_party(reporting_unit: XmlElement) -> Dict[str, int]:
    # Total votes for a party are the selection elements which have an AffiliationIdentifier as
    # a direct child element
    result = {}

    party_results = reporting_unit.findall(
        "./eml:Selection[eml:AffiliationIdentifier]", NAMESPACE
    )

    for party in party_results:
        party_name = party.find(
            "./eml:AffiliationIdentifier/eml:RegisteredName", NAMESPACE
        )
        if party_name is None or party_name.text is None:
            raise AttributeError(f"Party {party} had no registered name!")
        party_name = party_name.text

        party_result = party.find("eml:ValidVotes", NAMESPACE)
        if party_result is None or party_result.text is None:
            raise AttributeError(f"Party {party} had no associated votes!")
        party_result = int(party_result.text)

        result[party_name] = party_result

    return result
