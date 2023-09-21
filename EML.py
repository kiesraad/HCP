import xml_parser
import re
import protocol_checks
from zipfile import ZipFile
import re


class EML:
    def __init__(
        self, eml_file_id, main_unit_info, reporting_units_info, metadata=None
    ):
        self.eml_file_id = eml_file_id
        self.main_unit_info = main_unit_info
        self.reporting_units_info = reporting_units_info
        self.metadata = metadata

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
        reporing_units_info_list = [
            xml_parser.get_reporting_unit_info(reporting_unit)
            for reporting_unit in reporting_units
        ]
        reporting_units_info = {
            reporting_unit_info.get("reporting_unit_id"): reporting_unit_info
            for reporting_unit_info in reporing_units_info_list
        }

        # Fetch metadata of main EML
        metadata = xml_parser.get_metadata(xml_root)

        return EML(eml_file_id, main_unit_info, reporting_units_info, metadata)


class EMLZip:
    def __init__(self, eml: EML, odt):
        self.eml = eml
        self.odt = odt

    @staticmethod
    def from_zip(zip_path):
        with ZipFile(zip_path) as count_zip:
            eml = _find_and_parse_eml(count_zip)
            odt = _find_odt_content(count_zip)
            return EMLZip(eml=eml, odt=odt)

    def run_protocol(self):
        return {
            "eml_checks": self.eml.run_protocol(),
            "already_recounted": xml_parser.get_polling_stations_with_recounts(self.odt)
            if self.odt
            else [],
        }


def _find_and_parse_eml(zip: ZipFile):
    filelist = zip.namelist()
    telling_zip_pattern = re.compile(r"^Telling_.+\.zip$")
    eml_pattern = re.compile(r"^Telling_.+\.eml\.xml$")

    for filename in filelist:
        if telling_zip_pattern.match(filename):
            with zip.open(filename) as internal_zip_file:
                with ZipFile(internal_zip_file) as internal_zip:
                    internal_filelist = internal_zip.namelist()
                    for internal_file in internal_filelist:
                        if eml_pattern.match(internal_file):
                            eml_file = internal_zip.open(internal_file)
                            return EML.from_xml(eml_file)

    raise RuntimeError("No eml found in zipfile!")


def _find_odt_content(zip: ZipFile):
    filelist = zip.namelist()

    if "Model_Na31-1.odt" in filelist:
        with zip.open("Model_Na31-1.odt") as odt_file:
            return _extract_odt_xml_root(odt_file)

    return None


def _extract_odt_xml_root(odt_file):
    with ZipFile(odt_file) as odt_zip:
        with odt_zip.open("content.xml") as odt_xml:
            return xml_parser.parse_xml(odt_xml)
