import xml_parser
import re
import protocol_checks
from pprint import pprint


class EML:
    def __init__(
        self, eml_file_id, main_unit_info, reporting_units_info, metadata=None
    ):
        self.eml_file_id = eml_file_id
        self.main_unit_info = main_unit_info
        self.reporting_units_info = reporting_units_info
        self.metadata = metadata

    @classmethod
    def from_xml(cls, file_path):
        # Root element of the XML file
        xml_root = xml_parser.parse_xml(file_path)

        # EML id
        eml_file_id = xml_parser.get_eml_type(xml_root)
        # Check if EML is of type 510
        if not eml_file_id or not re.match("510[a-dqrs]", eml_file_id):
            raise ValueError(
                f"Tried to load EML with id {eml_file_id}, expected 510[a-dqrs]"
            )
        print(f"Loaded EML file {eml_file_id}")

        # XML elements with votes of the main unit (the unit itself) and
        # the reporting_units (subunits, so for GSB these are SBs, for HSB GSBs etc..)
        main_unit = xml_parser.get_main_unit(xml_root)
        reporting_units = xml_parser.get_reporting_units(xml_root)

        # Fetch vote information for main unit
        main_unit_info = xml_parser.get_reporting_unit_info(main_unit)

        # Fetch vote information for each individual subunit and index by reporting unit id
        reporing_units_info_list = [
            xml_parser.get_reporting_unit_info(reporting_unit)
            for reporting_unit in reporting_units
        ]
        reporting_units_info = {
            reporting_unit_info.get("reporting_unit_id"): reporting_unit_info
            for reporting_unit_info in reporing_units_info_list
        }

        return EML(eml_file_id, main_unit_info, reporting_units_info)

    def run_protocol(self):
        protocol_results = {}

        for polling_station_id, polling_station in self.reporting_units_info.items():
            result = {
                "zero_votes": protocol_checks.check_zero_votes(polling_station),
                "inexplicable_difference": protocol_checks.check_inexplicable_difference(
                    polling_station
                ),
                "high_invalid_vote_percentage": protocol_checks.check_too_many_rejected_votes(
                    polling_station, "ongeldig"
                ),
                "high_blank_vote_percentage": protocol_checks.check_too_many_rejected_votes(
                    polling_station, "blanco"
                ),
                "parties_with_high_difference_percentage": protocol_checks.check_parties_with_large_percentage_difference(
                    self.main_unit_info, polling_station
                ),
            }

            protocol_results[polling_station_id] = result

        return protocol_results
