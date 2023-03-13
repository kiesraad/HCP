import sys
import XMLparser
import process_info
import pprint
import csvWriter

tagPrefix = "{urn:oasis:names:tc:evs:schema:eml}"

pp = pprint


def main():
    # grab eml file
    items = XMLparser.find_eml_files()
    for item in items:
        xml = XMLparser.get_xml(item)

        # data on GSB niveau
        meta_data = XMLparser.get_meta_data(xml)
        total_votes_path = ["Count", "Election", "Contests", "Contest", "TotalVotes"]
        total_vote_structure = XMLparser.walk_xml_tree(xml, total_votes_path)
        total_raw_info = XMLparser.get_vote_info(total_vote_structure)

        # data on LSB niveau
        reporting_units = XMLparser.get_separate_entities_from_xml(xml)
        raw_info = XMLparser.get_vote_info_reporting_unit_array(reporting_units)

        # process info
        processed_info = {}
        for key in raw_info.keys():
            processed_info[key] = process_info.create_info(raw_info.get(key))

        # output info
        print("----------------------------------------")
        pp.pprint(total_raw_info)
        pp.pprint(raw_info)
        pp.pprint(processed_info)
        pp.pprint(meta_data)

        csvWriter.write_csv(raw_info, processed_info, meta_data)


if __name__ == '__main__':
    sys.exit(main())
