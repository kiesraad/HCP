import sys
import XMLparser
import process_info
import pprint

tagPrefix = "{urn:oasis:names:tc:evs:schema:eml}"

pp = pprint


def main():
    items = XMLparser.find_eml_files()
    xml = XMLparser.get_xml(items[0])
    reporting_units = XMLparser.get_separate_entities_from_xml(xml)
    total_vote_structure = [XMLparser.get_contest(xml).find(tagPrefix + "TotalVotes")]

    # total_raw_info is alle stemmen per partij opgeteld
    total_raw_info = XMLparser.get_vote_info(total_vote_structure).get(None)
    # raw_info is alle stemmen per partij per lokaal stembureau opgeteld
    raw_info = XMLparser.get_vote_info(reporting_units)

    pp.pprint(total_raw_info)
    pp.pprint(raw_info)

    processed_info = {}
    for key in raw_info.keys():
        processed_info[key] = process_info.create_info(raw_info.get(key))

    pp.pprint(processed_info)

    # todo put all info into csv


if __name__ == '__main__':
    sys.exit(main())
