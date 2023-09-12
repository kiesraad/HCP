from defusedxml import ElementTree as ET

NAMESPACE = {
    "eml": "urn:oasis:names:tc:evs:schema:eml",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "kr": "http://www.kiesraad.nl/extensions",
    "xal": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    "xnl": "urn:oasis:names:tc:ciq:xsdschema:xNL:2.0",
}


def get_text(xml_element):
    return xml_element.text if xml_element is not None else None


def get_attrib(xml_element, attrib_name):
    return xml_element.attrib.get(attrib_name) if xml_element is not None else None


def parse_xml(file_name):
    # EML should be checked so that it validates using the XSD

    tree = ET.parse(file_name)
    tree_root = tree.getroot()
    # Probably check if the root is of type EML here

    return tree_root


def get_eml_type(root):
    root_element = root.find(".")
    if root_element and root_element.tag == f"{{{NAMESPACE.get('eml')}}}EML":
        return get_attrib(root_element, "Id")

    return None


def get_reporting_units(xml):
    reporting_units = xml.findall(
        "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:ReportingUnitVotes",
        NAMESPACE,
    )

    # Probably check if the amount of reporting units > 0, otherwise the EML might have been
    # invalid, indicating a wrong structure, or the individual polling stations were not
    # included in the EML.

    return reporting_units


def get_main_unit(xml):
    main_unit = xml.find(
        "./eml:Count/eml:Election/eml:Contests/eml:Contest/eml:TotalVotes", NAMESPACE
    )

    return main_unit


def get_reporting_unit_info(reporting_unit):
    # Reporing unit element, which is present for the individual polling stations but
    # not for the 'total' count of the GSB
    reporting_unit_id_element = reporting_unit.find(
        "./eml:ReportingUnitIdentifier", NAMESPACE
    )

    reporting_unit_id = (
        reporting_unit_id_element.attrib.get("Id")
        if reporting_unit_id_element is not None
        else None
    )

    reporting_unit_name = (
        reporting_unit_id_element.text
        if reporting_unit_id_element is not None
        else None
    )

    # Get amount of eligible voters
    cast = int(reporting_unit.find("./eml:Cast", NAMESPACE).text)

    # Get total cast/counted votes
    total_counted = int(reporting_unit.find("./eml:TotalCounted", NAMESPACE).text)

    # Fetch invalid votes, the two types are mandatory
    # which are 'blanco' (blank) and 'ongeldig' (invalid)
    rejected_votes = get_vote_metadata_dict(reporting_unit, "./eml:RejectedVotes")

    # Fetch 'uncounted votes' which is metadata about the polling station
    uncounted_votes = get_vote_metadata_dict(reporting_unit, "./eml:UncountedVotes")

    # Fetch amount of votes per party
    votes_per_party = get_votes_per_party(reporting_unit)

    # Return dict of results
    return {
        "reporting_unit_id": reporting_unit_id,
        "reporting_unit_name": reporting_unit_name,
        "cast": cast,
        "total_counted": total_counted,
        "rejected_votes": rejected_votes,
        "uncounted_votes": uncounted_votes,
        "votes_per_party": votes_per_party,
    }


def get_vote_metadata_dict(reporting_unit, path):
    return {
        elem.attrib.get("ReasonCode"): int(elem.text)
        for elem in reporting_unit.findall(path, NAMESPACE)
    }


def get_votes_per_party(reporting_unit):
    # Total votes for a party are the selection elements which have an AffiliationIdentifier as
    # a direct child element
    return {
        party_result.find(
            "./eml:AffiliationIdentifier/eml:RegisteredName", NAMESPACE
        ).text: int(party_result.find("eml:ValidVotes", NAMESPACE).text)
        for party_result in reporting_unit.findall(
            "./eml:Selection[eml:AffiliationIdentifier]", NAMESPACE
        )
    }
