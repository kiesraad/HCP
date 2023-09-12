import xml_parser
import re


class Eml510:
    def __init__(self, file_path):
        """
        Create an eml object by specifying a file path to an EML_NL count file (510)

        Arguments:
            file_path -- path to the eml.xml file to load
        """
        # Root element of the XML file
        xml_root = xml_parser.parse_xml(file_path)

        # EML id
        self.eml_file_id = xml_parser.get_eml_type(xml_root)
        # Check if EML is of type 510
        if not self.eml_file_id or not re.match("510[a-dqrs]", self.eml_file_id):
            raise ValueError(
                f"Tried to load EML with id {self.eml_file_id}, expected 510[a-dqrs]"
            )

        print(f"Loaded EML file {self.eml_file_id}")

        # XML elements with votes of the main unit (the unit itself) and
        # the reporting_units (subunits, so for GSB these are SBs, for HSB GSBs etc..)
        main_unit = xml_parser.get_main_unit(xml_root)
        reporting_units = xml_parser.get_reporting_units(xml_root)

        # Fetch vote information for main unit
        self.main_unit_info = xml_parser.get_reporting_unit_info(main_unit)

        # Fetch vote information for each individual subunit and index by reporting unit id
        reporing_units_info_list = [
            xml_parser.get_reporting_unit_info(reporting_unit)
            for reporting_unit in reporting_units
        ]
        self.reporting_units_info = {
            reporting_unit_info.get("reporting_unit_id"): reporting_unit_info
            for reporting_unit_info in reporing_units_info_list
        }
