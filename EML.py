import xml_parser
import re
import protocol_checks
from dataclasses import dataclass
from typing import Dict
from eml_types import EmlMetadata, ReportingUnitInfo
import re


@dataclass
class EML:
    eml_file_id: str
    main_unit_info: ReportingUnitInfo
    reporting_units_info: Dict[str, ReportingUnitInfo]
    metadata: EmlMetadata

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
                "high_explained_difference_percentage": protocol_checks.check_too_many_explained_differences(
                    polling_station
                ),
                "parties_with_high_difference_percentage": protocol_checks.check_parties_with_large_percentage_difference(
                    self.main_unit_info, polling_station
                ),
                "party_difference_percentages": protocol_checks.get_party_difference_percentages(
                    self.main_unit_info, polling_station
                ),
            }

            protocol_results[polling_station_id] = result

        return protocol_results

    @staticmethod
    def from_xml(file_path):
        # Root element of the XML file
        xml_root = xml_parser.parse_xml(file_path)

        # EML id
        eml_file_id = xml_parser.get_eml_type(xml_root)
        # Check if EML is of type 510
        if not eml_file_id or not re.match("510[a-dqrs]", eml_file_id):
            raise ValueError(
                f"Tried to load EML with id {eml_file_id}, expected 510[a-dqrs]"
            )

        # XML elements with votes of the main unit (the unit itself) and
        # the reporting_units (subunits, so for GSB these are SBs, for HSB GSBs etc..)
        main_unit = xml_parser.get_main_unit(xml_root)
        reporting_units = xml_parser.get_reporting_units(xml_root)

        # Fetch vote information for main unit
        main_unit_info = xml_parser.get_reporting_unit_info(main_unit)

        # Fetch vote information for each individual subunit and index by reporting unit id
        reporting_units_info = {}
        for reporting_unit in reporting_units:
            info = xml_parser.get_reporting_unit_info(reporting_unit)
            if info.reporting_unit_id is None:
                raise AttributeError(
                    f"Tried to add reporting unit {reporting_unit} without ID!"
                )
            reporting_units_info[info.reporting_unit_id] = info

        # Fetch metadata of main EML
        metadata = xml_parser.get_metadata(xml_root)

        return EML(eml_file_id, main_unit_info, reporting_units_info, metadata)
