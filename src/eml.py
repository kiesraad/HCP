from neighbourhood import ReportingNeighbourhoods
import xml_parser
import re
import protocol_checks
from dataclasses import dataclass
from typing import Dict, List, Optional, ClassVar
from eml_types import (
    EmlMetadata,
    ReportingUnitInfo,
    PartyIdentifier,
    InvalidEmlException,
    VoteDifference,
    SwitchedCandidate,
)


@dataclass
class CheckResult:
    zero_votes: bool
    inexplicable_difference: int
    explanation_sum_difference: int
    high_invalid_vote_percentage: Optional[float]
    high_blank_vote_percentage: Optional[float]
    high_vote_difference: Optional[VoteDifference]
    parties_with_high_difference_percentage: List[str]
    party_difference_percentages: Dict[PartyIdentifier, float]
    potentially_switched_candidates: List[SwitchedCandidate]
    already_recounted: bool


@dataclass
class EML:
    eml_file_id: str
    main_unit_info: ReportingUnitInfo
    reporting_units_info: Dict[str, ReportingUnitInfo]
    metadata: EmlMetadata

    INVALID_VOTE_THRESHOLD_PCT: ClassVar[float] = 3.0
    BLANK_VOTE_THRESHOLD_PCT: ClassVar[float] = 3.0

    DIFF_VOTE_THRESHOLD_PCT: ClassVar[float] = 1.0
    DIFF_VOTE_THRESHOLD: ClassVar[int] = 10

    PARTY_DIFFERENCE_THRESHOLD_PCT: ClassVar[float] = 50.0

    # Switched candidate parameters
    MINIMUM_REPORTING_UNITS_MUNICIPALITY: ClassVar[int] = 2
    MINIMUM_REPORTING_UNITS_NEIGHBOURHOOD: ClassVar[int] = 5
    MINIMUM_DEVIATION_FACTOR: ClassVar[int] = 10
    MINIMUM_VOTES: ClassVar[int] = 20

    def run_protocol(
        self, reporting_neighbourhoods: Optional[ReportingNeighbourhoods] = None
    ) -> Dict[str, CheckResult]:
        protocol_results = {}

        for polling_station_id, polling_station in self.reporting_units_info.items():
            neighbourhood_reference_group = (
                (reporting_neighbourhoods.get_reference_group(polling_station_id))
                if reporting_neighbourhoods
                else None
            )

            potentially_switched_municipality_candidates = (
                protocol_checks.get_potentially_switched_candidates(
                    self.main_unit_info,
                    polling_station,
                    amount_of_reporting_units=self.metadata.reporting_unit_amount,
                    minimum_reporting_units=EML.MINIMUM_REPORTING_UNITS_MUNICIPALITY,
                    minimum_deviation_factor=EML.MINIMUM_DEVIATION_FACTOR,
                    minimum_votes=EML.MINIMUM_VOTES,
                )
            )

            potentially_switched_neighbourhood_candidates = (
                protocol_checks.get_potentially_switched_candidates(
                    neighbourhood_reference_group,
                    polling_station,
                    amount_of_reporting_units=reporting_neighbourhoods.get_reference_size(
                        polling_station_id
                    ),
                    minimum_reporting_units=EML.MINIMUM_REPORTING_UNITS_NEIGHBOURHOOD,
                    minimum_deviation_factor=EML.MINIMUM_DEVIATION_FACTOR,
                    minimum_votes=EML.MINIMUM_VOTES,
                )
                if neighbourhood_reference_group and reporting_neighbourhoods
                else None
            )

            potentially_switched_candidates = (
                protocol_checks.get_switched_candidate_combination(
                    potentially_switched_municipality_candidates,
                    potentially_switched_neighbourhood_candidates,
                )
            )

            check_result = CheckResult(
                zero_votes=protocol_checks.check_zero_votes(polling_station),
                inexplicable_difference=protocol_checks.check_inexplicable_difference(
                    polling_station
                ),
                explanation_sum_difference=protocol_checks.check_explanation_sum_difference(
                    polling_station
                ),
                high_invalid_vote_percentage=protocol_checks.check_too_many_rejected_votes(
                    polling_station, "ongeldig", EML.INVALID_VOTE_THRESHOLD_PCT
                ),
                high_blank_vote_percentage=protocol_checks.check_too_many_rejected_votes(
                    polling_station, "blanco", EML.BLANK_VOTE_THRESHOLD_PCT
                ),
                high_vote_difference=protocol_checks.check_too_many_differences(
                    polling_station,
                    EML.DIFF_VOTE_THRESHOLD_PCT,
                    EML.DIFF_VOTE_THRESHOLD,
                ),
                parties_with_high_difference_percentage=protocol_checks.check_parties_with_large_percentage_difference(
                    self.main_unit_info,
                    polling_station,
                    EML.PARTY_DIFFERENCE_THRESHOLD_PCT,
                ),
                party_difference_percentages=protocol_checks.get_party_difference_percentages(
                    self.main_unit_info, polling_station
                ),
                potentially_switched_candidates=potentially_switched_candidates,
                already_recounted=False,
            )

            protocol_results[polling_station_id] = check_result

        return protocol_results

    @staticmethod
    def from_xml(file_path):
        # Root element of the XML file
        xml_root = xml_parser.parse_xml(file_path)

        # EML id
        eml_file_id = xml_parser.get_eml_type(xml_root)
        # Check if EML is of type 510
        if not eml_file_id or not re.match("510[a-dqrs]", eml_file_id):
            raise InvalidEmlException(
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
                raise InvalidEmlException(
                    f"Tried to add reporting unit {reporting_unit} without ID!"
                )
            reporting_units_info[info.reporting_unit_id] = info

        # Fetch metadata of main EML
        metadata = xml_parser.get_metadata(xml_root)

        return EML(eml_file_id, main_unit_info, reporting_units_info, metadata)
