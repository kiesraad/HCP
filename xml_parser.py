from defusedxml import ElementTree as ET

NAMESPACE = {
    "eml": "urn:oasis:names:tc:evs:schema:eml",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "kr": "http://www.kiesraad.nl/extensions",
    "xal": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    "xnl": "urn:oasis:names:tc:ciq:xsdschema:xNL:2.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
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


def get_metadata(root):
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

    return {
        "creation_date_time": creation_date_time,
        "authority_id": authority_id,
        "authority_name": authority_name,
        "election_id": election_id,
        "election_name": election_name,
        "election_domain": election_domain,
        "election_date": election_date,
        "contest_identifier": contest_identifier,
        "reporting_unit_names": reporting_unit_names,
    }


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


## PV code
def get_polling_stations_with_recounts(odt_root):
    recounts = []

    polling_stations = odt_root.findall(
        "./office:body/office:text/table:table[@table:name='NieuweTelling']/table:table-row",
        NAMESPACE,
    )

    for polling_station in polling_stations:
        # Get three different span elements which describe the polling station
        # the first contains the id, the second the name and the third optionally
        # the zip code
        polling_station_descriptors = polling_station.findall(
            ".//text:span[@text:description]", NAMESPACE
        )

        polling_station_id = get_text(polling_station_descriptors[0])
        polling_station_name = get_text(polling_station_descriptors[1])
        polling_station_zip = get_text(polling_station_descriptors[2])

        recounts.append(
            {
                "polling_station_id": polling_station_id,
                "polling_station_name": polling_station_name,
                "polling_station_zip": polling_station_zip,
                "polling_station_name_joined": f"{polling_station_name} {polling_station_zip}"
                if polling_station_zip
                else polling_station_name,
            }
        )

    return recounts
