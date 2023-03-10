from defusedxml.ElementTree import parse
from os import listdir
tagPrefix = "{urn:oasis:names:tc:evs:schema:eml}"

global_xml = ""
current_file = ""


def get_separate_entities_from_xml(xml):
    contest = get_contest(xml)
    return contest.findall(tagPrefix + "ReportingUnitVotes")


def get_xml(file_name):
    global global_xml
    global current_file

    if global_xml == "" and current_file != file_name:
        current_file = file_name
        tree = parse("./data/" + file_name)
        global_xml = tree.getroot()
        return get_xml(file_name)
    else:
        return global_xml


def get_contest(xml):
    count = xml.find(tagPrefix + "Count")
    election = count.find(tagPrefix + "Election")
    contests = election.find(tagPrefix + "Contests")
    return contests.find(tagPrefix + "Contest")


def get_vote_info(reporting_units):
    info_dict = {}
    for reporting_unit in reporting_units:
        reporting_unit_dict = {}
        # these ranges map to the required info
        for z in range(12, 14):
            reporting_unit_dict[reporting_unit[-z].attrib.get("ReasonCode")] = reporting_unit[-z].text
        # these ranges map to the required info
        for z in range(14, 15):
            reporting_unit_dict[reporting_unit[-z].tag.replace(tagPrefix, "")] = reporting_unit[-z].text
        for selection in reporting_unit.findall(tagPrefix+"Selection"):
            party_identifier = selection.find(tagPrefix+"AffiliationIdentifier")
            if party_identifier:
                party_name = party_identifier.find(tagPrefix + "RegisteredName").text
                reporting_unit_dict[party_name] = int(selection.find(tagPrefix+"ValidVotes").text)
        if reporting_unit.find(tagPrefix+"ReportingUnitIdentifier"):
            reporting_unit_dict["name"] = reporting_unit.find(tagPrefix+"ReportingUnitIdentifier").text
        info_dict[reporting_unit[0].attrib.get("Id")] = reporting_unit_dict

    return info_dict


# todo, for eventual deployment the ./data path specifier must be removed
def find_eml_files():
    file_list = listdir("./data")
    for item in file_list:
        if ".xml" not in item:
            file_list.remove(item)
    return file_list
