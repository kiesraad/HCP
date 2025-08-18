import re
from typing import IO, Dict, List, Optional, Tuple, Union
from xml.etree.ElementTree import Element as XmlElement

from defusedxml import ElementTree as ET

from eml_types import (
    CandidateIdentifier,
    EmlMetadata,
    InvalidEmlException,
    PartyIdentifier,
    ReportingUnitInfo,
)

NAMESPACE = {
    "eml": "urn:oasis:names:tc:evs:schema:eml",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "kr": "http://www.kiesraad.nl/extensions",
    "xal": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    "xnl": "urn:oasis:names:tc:ciq:xsdschema:xNL:2.0",
}
ZIP_REGEX = re.compile(r"\(postcode: (\d{4} \w{2})\)")


def parse_xml(file_name: Union[str, IO[bytes]]) -> XmlElement:
    """Fetch the root node of an EML XML DOM-tree given a filepath.

    Args:
        file_name: Path to the EML file to parse.

    Returns:
        Root node of the EML file.
    """
    tree = ET.parse(file_name)
    tree_root = tree.getroot()

    if tree_root is None:
        raise InvalidEmlException(f"{file_name} could not be parsed as XML")

    return tree_root


def get_eml_type(root: XmlElement) -> Optional[str]:
    """Fetches the EML ID.

    Args:
        root: The root node to query.

    Returns:
        The ID of the EML file (e.g. `"510b"` for municipality counts).
    """
    root_element = root.find(".")
    if root_element is not None and root_element.tag == f"{{{NAMESPACE.get('eml')}}}EML":
        return _get_attrib(root_element, "Id")

    return None


def get_metadata(root: XmlElement) -> EmlMetadata:
    """Given the root of the EML DOM-tree, construct an instance of `EmlMetadata`.

    Args:
        root: The root node to query.

    Returns:
        `EmlMetadata` instance containing all EML metadata.
    """
    creation_date_time = _get_text(root.find("./kr:CreationDateTime", NAMESPACE))
    authority_id = _get_attrib(
        root.find(
            "./eml:ManagingAuthority/eml:AuthorityIdentifier",
            NAMESPACE,
        ),
        "Id",
    )
    authority_name = _get_text(
        root.find(
            "./eml:ManagingAuthority/eml:AuthorityIdentifier",
            NAMESPACE,
        )
    )
    election_id = _get_attrib(
        root.find("./eml:Count/eml:Election/eml:ElectionIdentifier", NAMESPACE), "Id"
    )
    election_name = _get_text(
        root.find(
            "./eml:Count/eml:Election/eml:ElectionIdentifier/eml:ElectionName",
            NAMESPACE,
        )
    )
    election_domain = _get_text(
        root.find(
            "./eml:Count/eml:Election/eml:ElectionIdentifier/kr:ElectionDomain",
            NAMESPACE,
        ),
    )
    election_date = _get_text(
        root.find(
            "./eml:Count/eml:Election/eml:ElectionIdentifier/kr:ElectionDate",
            NAMESPACE,
        )
    )
    contest_identifier = _get_attrib(
        root.find(
            "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:ContestIdentifier",
            NAMESPACE,
        ),
        "Id",
    )

    reporting_units = root.findall(".//eml:ReportingUnitIdentifier", NAMESPACE)
    reporting_unit_names = {
        _get_mandatory_attrib(elem, "Id"): _get_text(elem) for elem in reporting_units
    }
    reporting_unit_zips = {
        reporting_unit_id: _extract_zip_from_name(reporting_unit_name)
        for (reporting_unit_id, reporting_unit_name) in reporting_unit_names.items()
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
        reporting_unit_amount=len(reporting_units),
        reporting_unit_names=reporting_unit_names,
        reporting_unit_zips=reporting_unit_zips,
    )


def get_reporting_units(xml: XmlElement) -> List[XmlElement]:
    """Helper function to return a list of all reporting unit nodes in the EML.

    Args:
        xml: The XML node to query.

    Returns:
        List of XML reporting unit nodes.
    """
    reporting_units = xml.findall(
        "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:ReportingUnitVotes",
        NAMESPACE,
    )

    # Probably check if the amount of reporting units > 0, otherwise the EML might have been
    # invalid, indicating a wrong structure, or the individual polling stations were not
    # included in the EML.

    return reporting_units


def get_main_unit(xml: XmlElement) -> XmlElement:
    """Helper function to return main unit node in the EML.

    Args:
        xml: The XML node to query.

    Returns:
        The main unit XML node.
    """
    main_unit = xml.find(
        "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:TotalVotes", NAMESPACE
    )

    if main_unit is None:
        raise AttributeError("EML had no main reporting unit!")

    return main_unit


def get_reporting_unit_info(reporting_unit: XmlElement) -> ReportingUnitInfo:
    """Given a reporting unit EML node, construct a `ReportingUnitInfo` instance.

    Args:
        reporting_unit: The reporting unit node to turn into a `ReportingUnitInfo` instance.

    Returns:
        The `ReportingUnitInfo` instance.
    """
    # Reporing unit element, which is present for the individual polling stations but
    # not for the 'total' count of the GSB
    reporting_unit_id_element = reporting_unit.find(
        "./eml:ReportingUnitIdentifier", NAMESPACE
    )
    reporting_unit_id = _get_attrib(reporting_unit_id_element, "Id")
    reporting_unit_name = _get_text(reporting_unit_id_element)

    # Get amount of eligible voters
    cast = int(_get_mandatory_text(reporting_unit.find("./eml:Cast", NAMESPACE)))

    # Get total cast/counted votes
    total_counted = int(
        _get_mandatory_text(reporting_unit.find("./eml:TotalCounted", NAMESPACE))
    )

    # Fetch invalid votes, the two types are mandatory
    # which are 'blanco' (blank) and 'ongeldig' (invalid)
    rejected_votes = _get_vote_metadata_dict(reporting_unit, "./eml:RejectedVotes")

    # Fetch 'uncounted votes' which is metadata about the polling station
    uncounted_votes = _get_vote_metadata_dict(reporting_unit, "./eml:UncountedVotes")

    # Fetch amount of votes per party
    (votes_per_party, votes_per_candidate) = _get_party_and_candvotes(reporting_unit)

    return ReportingUnitInfo(
        reporting_unit_id=reporting_unit_id,
        reporting_unit_name=reporting_unit_name,
        cast=cast,
        total_counted=total_counted,
        rejected_votes=rejected_votes,
        uncounted_votes=uncounted_votes,
        votes_per_party=votes_per_party,
        votes_per_candidate=votes_per_candidate,
    )


def _get_text(xml_element: Optional[XmlElement]) -> Optional[str]:
    return xml_element.text if xml_element is not None else None


def _get_mandatory_text(xml_element: Optional[XmlElement]) -> str:
    if xml_element is None:
        raise ValueError("Could not find specified XML element")

    text = xml_element.text
    if text is None:
        raise AttributeError(
            f"Element {xml_element} did not have text but was mandatory"
        )

    return text


def _get_attrib(xml_element: Optional[XmlElement], attrib_name: str) -> Optional[str]:
    return xml_element.attrib.get(attrib_name) if xml_element is not None else None


def _get_mandatory_attrib(xml_element: Optional[XmlElement], attrib_name: str) -> str:
    if xml_element is None:
        raise ValueError("Could not find specified XML element")

    attrib = xml_element.attrib.get(attrib_name)
    if attrib is None:
        raise AttributeError(
            f"Element {xml_element} did not have attribute {attrib_name} but was mandatory"
        )

    return attrib


def _extract_zip_from_name(reporting_unit_name: Optional[str]) -> Optional[str]:
    if reporting_unit_name is None:
        return None
    search_result = re.search(ZIP_REGEX, reporting_unit_name)
    if search_result is None:
        return None
    search_groups = search_result.groups()
    if len(search_groups) != 1:
        return None
    return search_groups[0].replace(" ", "")


def _get_vote_metadata_dict(reporting_unit: XmlElement, path: str) -> Dict[str, int]:
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


def _get_party_and_candvotes(
    reporting_unit: XmlElement,
) -> Tuple[Dict[PartyIdentifier, int], Dict[CandidateIdentifier, int]]:
    party_votes_dict: Dict[PartyIdentifier, int] = {}
    cand_votes_dict: Dict[CandidateIdentifier, int] = {}

    current_party_identifier = None

    for count in reporting_unit.findall("./eml:Selection", NAMESPACE):
        party_identifier_elem = count.find("./eml:AffiliationIdentifier", NAMESPACE)
        candidate_identifier_elem = count.find(
            "./eml:Candidate/eml:CandidateIdentifier", NAMESPACE
        )

        # Selection element contains either a party identifier or candidate identifier
        if party_identifier_elem is not None:
            party_id = party_identifier_elem.attrib.get("Id")
            if party_id is None:
                raise InvalidEmlException

            party_id = int(party_id)
            party_name = _get_text(
                party_identifier_elem.find("./eml:RegisteredName", NAMESPACE)
            )

            # Set the current party identifier for upcoming candidate selection elements
            current_party_identifier = PartyIdentifier(id=party_id, name=party_name)
            party_votes_elem = count.find("eml:ValidVotes", NAMESPACE)
            if party_votes_elem is None or party_votes_elem.text is None:
                raise InvalidEmlException
            party_votes = int(party_votes_elem.text)

            party_votes_dict[current_party_identifier] = party_votes

        elif party_identifier_elem is None and candidate_identifier_elem is not None:
            if current_party_identifier is None:
                raise InvalidEmlException

            candidate_id = candidate_identifier_elem.attrib.get("Id")
            if candidate_id is None:
                raise InvalidEmlException
            candidate_id = int(candidate_id)
            candidate_identifier = CandidateIdentifier(
                party=current_party_identifier, cand_id=candidate_id
            )

            candidate_votes_elem = count.find("eml:ValidVotes", NAMESPACE)
            if candidate_votes_elem is None or candidate_votes_elem.text is None:
                raise InvalidEmlException
            candidate_votes = int(candidate_votes_elem.text)

            cand_votes_dict[candidate_identifier] = candidate_votes

        else:
            raise InvalidEmlException

    return (party_votes_dict, cand_votes_dict)
