import re
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Dict, List, Optional

import protocol_checks
import xml_parser
from eml_types import (
    EmlMetadata,
    InvalidEmlException,
    PartyIdentifier,
    ReportingUnitInfo,
    SwitchedCandidate,
    SwitchedCandidateConfig,
    VoteDifference,
)
from neighbourhood import NeighbourhoodData, ReportingNeighbourhoods


class SummaryType(Enum):
    A = "A"
    B = "B"


@dataclass
class CheckResult:
    """Container representing the result of running all checks
    on a given EML file.
    """

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

    def summarise(self, summary_type: SummaryType) -> str:
        def prefix(n_findings: int) -> str:
            if n_findings == 0:
                return " "
            elif n_findings == 1:
                return " Daarnaast "
            else:
                return " Ook "

        class Sentence:
            def __init__(self) -> None:
                self.content = ["In dit stembureau"]
                self.n_findings = 0

            def add(self, text: str) -> None:
                self.content += f"{prefix(self.n_findings)}{text}."
                self.n_findings += 1

            def render(self, recounted: bool) -> str:
                if self.n_findings == 0:
                    return f"{self.content} zijn er geen bevindingen."
                return f"{''.join(self.content)} Er is {'wel' if recounted else 'niet'} herteld."

        sentence = Sentence()

        if summary_type == SummaryType.A:
            if self.inexplicable_difference:
                sentence.add(
                    f"is er een onverklaard verschil van {self.inexplicable_difference}"
                )
            if self.explanation_sum_difference:
                sentence.add(
                    f"is er een verschil tussen het aantal toegelaten kiezers en de som van de gegeven verklaringen van {self.explanation_sum_difference}"
                )
        elif summary_type == SummaryType.B:
            if self.zero_votes:
                sentence.add("zijn er 0 stemmen uitgebracht")
            if self.high_invalid_vote_percentage:
                sentence.add(
                    f"is er een hoog percentage ongeldige stemmen ({int(self.high_invalid_vote_percentage)}%)"
                )
            if self.high_blank_vote_percentage:
                sentence.add(
                    f"is er een hoog percentage blanco stemmen ({int(self.high_blank_vote_percentage)}%)"
                )
            if self.high_vote_difference:
                sentence.add(
                    f"is er een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen ({self.high_vote_difference})"
                )
            if self.parties_with_high_difference_percentage:
                sentence.add(
                    f"hebben de volgende partijen een opmerkelijk grote afwijking ten opzichte van het gemeentegemiddelde: {', '.join(self.parties_with_high_difference_percentage)}"
                )
            if self.potentially_switched_candidates:
                sentence.add(
                    f"is er een mogelijke verwisseling bij de volgende kandidaten: {', '.join((str(switch) for switch in self.potentially_switched_candidates))}"
                )

        return sentence.render(self.already_recounted)


@dataclass
class EML:
    """Main container for all information which has been loaded from an .eml.xml file.
    Contains all the necessary information for running all checks, and additionally
    contains the configuration for all the checks.
    """

    eml_file_id: str
    main_unit_info: ReportingUnitInfo
    reporting_units_info: Dict[str, ReportingUnitInfo]
    metadata: EmlMetadata

    # Config ---
    INVALID_VOTE_THRESHOLD_PCT: ClassVar[float] = 3.0
    BLANK_VOTE_THRESHOLD_PCT: ClassVar[float] = 3.0

    DIFF_VOTE_THRESHOLD_PCT: ClassVar[float] = 2.0
    DIFF_VOTE_THRESHOLD: ClassVar[int] = 15

    PARTY_DIFFERENCE_THRESHOLD_PCT: ClassVar[float] = 50.0

    SWITCHED_CANDIDATE_CONFIG: ClassVar[SwitchedCandidateConfig] = (
        SwitchedCandidateConfig(
            minimum_reporting_units_municipality=2,
            minimum_reporting_units_neighbourhood=5,
            minimum_deviation_factor=10,
            minimum_votes=20,
        )
    )
    # ---

    def run_protocol(
        self, neighbourhood_data: Optional[NeighbourhoodData] = None
    ) -> Dict[str, CheckResult]:
        """Run all specified protocol checks on this EML instance.

        Args:
            neighbourhood_data: If NeighbourhoodData is specified, also run some checks at neighbourhood level.

        Returns:
            Dictionary mapping reporting unit ids to resulting CheckResults obtained by running all checks
        """
        # Generate reporting neighbourhoods data which can be reused for all individual
        # polling stations
        reporting_neighbourhoods: Optional[ReportingNeighbourhoods] = (
            neighbourhood_data.fetch_reporting_neighbourhoods(
                self.metadata.reporting_unit_zips, self.reporting_units_info
            )
            if neighbourhood_data
            else None
        )

        protocol_results = {}

        for polling_station_id, polling_station in self.reporting_units_info.items():
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
                potentially_switched_candidates=protocol_checks.check_potentially_switched_candidates(
                    polling_station_id,
                    self.main_unit_info,
                    polling_station,
                    self.metadata.reporting_unit_amount,
                    reporting_neighbourhoods,
                    EML.SWITCHED_CANDIDATE_CONFIG,
                ),
                already_recounted=False,
            )

            protocol_results[polling_station_id] = check_result

        return protocol_results

    @staticmethod
    def from_xml(file_path: str) -> "EML":
        """Static method for constructing an instance of the EML class
        from a given file_path

        Args:
            file_path: Path to the .eml.xml file to read.

        Raises:
            InvalidEmlException: when specified .eml.xml is of incorrect type.
            InvalidEmlException: when any reporting unit does not have an id.

        Returns:
            EML class instance with all relevant data to run the protocol checks.
        """
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
