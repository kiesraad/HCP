from defusedxml.ElementTree import parse

tagPrefix = "{urn:oasis:names:tc:evs:schema:eml}"
krPrefix = "{http://www.kiesraad.nl/extensions}"


def get_xml(file_name):
    tree = parse(file_name)
    return tree.getroot()


def get_separate_entities_from_xml(xml):
    path = ["Count", "Election", "Contests", "Contest"]
    contest = walk_xml_tree(xml, path)
    return contest.findall(tagPrefix + "ReportingUnitVotes")


def walk_xml_tree(xml_root, path):
    xml = xml_root
    if len(path) > 0:
        for leave in path:
            xml = xml.find(tagPrefix + leave)
    return xml


def get_vote_info_reporting_unit_array(reporting_units):
    info_dict = {}
    for reporting_unit in reporting_units:
        info_dict[reporting_unit[0].attrib.get("Id")] = get_vote_info(reporting_unit)
    return info_dict


def get_vote_info(unit):
    reporting_unit_dict = {}

    reporting_unit_dict["uncounted_votes"] = get_rejected_and_uncounted_votes(unit)
    reporting_unit_dict["party_vote_count"] = get_vote_count_per_party(unit)
    reporting_unit_dict["TotalCounted"] = int(
        walk_xml_tree(unit, ["TotalCounted"]).text
    )

    if unit.find(tagPrefix + "ReportingUnitIdentifier") is not None:
        reporting_unit_dict["name"] = unit.find(
            tagPrefix + "ReportingUnitIdentifier"
        ).text
    return reporting_unit_dict


def get_rejected_and_uncounted_votes(reporting_unit):
    rejected_and_uncounted_votes = {}
    for RejectedVotes_and_UncountedVotes in reporting_unit:
        reason = RejectedVotes_and_UncountedVotes.get("ReasonCode")
        amount = RejectedVotes_and_UncountedVotes.text
        if reason:
            rejected_and_uncounted_votes[reason] = amount
    return rejected_and_uncounted_votes


def get_vote_count_per_party(reporting_unit):
    party_vote_count = {}
    for selection in reporting_unit.findall(tagPrefix + "Selection"):
        party_identifier = selection.find(tagPrefix + "AffiliationIdentifier")
        if party_identifier:
            party_name = party_identifier.find(tagPrefix + "RegisteredName").text
            vote_count = int(selection.find(tagPrefix + "ValidVotes").text)
            party_vote_count[party_name] = vote_count

    return party_vote_count


def get_meta_data(xml):
    path = ["Count", "Election", "ElectionIdentifier"]
    election_identification = walk_xml_tree(xml, path)

    try:
        creationdatetime = xml.find(krPrefix + "CreationDateTime").text
    except AttributeError:
        creationdatetime = ""

    try:
        electionname = election_identification.find(tagPrefix + "ElectionName").text
    except AttributeError:
        electionname = ""
    try:
        electiondomain = election_identification.find(krPrefix + "ElectionDomain").text
    except AttributeError:
        electiondomain = ""
    try:
        electiondate = election_identification.find(krPrefix + "ElectionDate").text
    except AttributeError:
        electiondate = ""

    meta_data = {
        "id": xml.find(tagPrefix + "ManagingAuthority")
        .find(tagPrefix + "AuthorityIdentifier")
        .attrib.get("Id"),
        "eml_date": creationdatetime,
        "name": electionname,
        "gebied": electiondomain,
        "date": electiondate,
    }

    return meta_data
