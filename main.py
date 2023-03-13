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
        total_vote_path = ["Count", "Election", "Contests", "Contest", "TotalVotes"]
        total_vote_xml = XMLparser.walk_xml_tree(xml, total_vote_path)
        total_raw_info = XMLparser.get_vote_info(total_vote_xml)

        # data on LSB niveau
        reporting_units = XMLparser.get_separate_entities_from_xml(xml)
        reporting_units_info = XMLparser.get_vote_info_reporting_unit_array(reporting_units)


        # process info
        afwijkingen = process_info.process_50_afwijking(total_raw_info, reporting_units_info)
        processed_info = process_info.create_info_array(reporting_units_info, afwijkingen)

        # print("----------------------------------------")
        # pp.pprint(total_raw_info)
        # pp.pprint(reporting_units_info)
        # pp.pprint(processed_info)
        # pp.pprint(meta_data)

        csvWriter.write_csv(reporting_units_info, processed_info, meta_data)
        csvWriter.write_afwijkeningen(meta_data, afwijkingen, reporting_units_info)


if __name__ == '__main__':
    sys.exit(main())
