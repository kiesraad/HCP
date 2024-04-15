from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union


@dataclass
class EmlMetadata:
    """Dataclass which holds EML metadata like the creation_date_time of
    the EML file or derived mappings from reporting_unit_id to zip or name.
    """

    creation_date_time: Optional[str]
    authority_id: Optional[str]
    authority_name: Optional[str]
    election_id: Optional[str]
    election_name: Optional[str]
    election_domain: Optional[str]
    election_date: Optional[str]
    contest_identifier: Optional[str]
    reporting_unit_amount: int
    reporting_unit_names: Dict[str, Optional[str]]
    reporting_unit_zips: Dict[str, Optional[str]]


@dataclass(frozen=True, order=True)
class PartyIdentifier:
    """Party identifier used for matching parties in dicts."""

    id: int
    name: Optional[str]


@dataclass(frozen=True, order=True)
class CandidateIdentifier:
    """Candidate identifier used for matching candidates in dicts."""

    party: PartyIdentifier
    cand_id: int


@dataclass
class ReportingUnitInfo:
    """Container which holds the main information for a given reporting unit, containing
    vote counts at candidate and party level, and information about those votes
    (amount of blank votes, invalid votes etc..)
    """

    reporting_unit_id: Optional[str]
    reporting_unit_name: Optional[str]
    cast: int
    total_counted: int
    rejected_votes: Dict[str, int]
    uncounted_votes: Dict[str, int]
    votes_per_party: Dict[PartyIdentifier, int]
    votes_per_candidate: Dict[CandidateIdentifier, int]


@dataclass
class VoteDifferenceAmount:
    """Simple wrapper for int value."""

    value: int

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class VoteDifferencePercentage:
    """Simple wrapper for float value."""

    value: float

    def __str__(self) -> str:
        return f"{round(self.value, 1)}%"


VoteDifference = Union[VoteDifferenceAmount, VoteDifferencePercentage]


@dataclass
class SwitchedCandidate:
    """Container representing a potentially switched candidate."""

    candidate_with_fewer: CandidateIdentifier
    candidate_with_fewer_received: int
    candidate_with_fewer_expected: int
    candidate_with_more: CandidateIdentifier
    candidate_with_more_received: int
    candidate_with_more_expected: int

    def __str__(self) -> str:
        party_name = (
            f" ({self.candidate_with_more.party.name})"
            if self.candidate_with_more.party.name
            else ""
        )
        return (
            f"Mogelijke verwisseling op lijst {self.candidate_with_more.party.id}{party_name}: "
            f"Kandidaat {self.candidate_with_more.cand_id} had {self.candidate_with_more_received} stemmen "
            f"maar verwachting was {self.candidate_with_more_expected}. "
            f"Kandidaat {self.candidate_with_fewer.cand_id} had {self.candidate_with_fewer_received} stemmen "
            f"maar verwachting was {self.candidate_with_fewer_expected}"
        )


@dataclass
class SwitchedCandidateConfig:
    """Container for configuration parameters for the switched candidate
    check
    """

    minimum_reporting_units_municipality: int
    minimum_reporting_units_neighbourhood: int
    minimum_deviation_factor: int
    minimum_votes: int


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
                return "Er is "
            elif n_findings == 1:
                return " Daarnaast is er "
            else:
                return " Ook is er "

        class Sentence:
            def __init__(self) -> None:
                self.content = []
                self.n_findings = 0

            def add(self, text: str) -> None:
                self.content += f"{prefix(self.n_findings)}{text}."
                self.n_findings += 1

            def render(self, recounted: bool) -> str:
                if self.n_findings == 0:
                    return "Er zijn geen bevindingen."
                return f"{''.join(self.content)} Er is {'wel' if recounted else 'niet'} herteld."

        sentence = Sentence()

        if summary_type == SummaryType.A:
            if self.inexplicable_difference:
                sentence.add(
                    f"een onverklaard verschil van {self.inexplicable_difference}"
                )
            if self.explanation_sum_difference:
                sentence.add(
                    f"een aantal ontbrekende verklaringen van {self.explanation_sum_difference}"
                )
        elif summary_type == SummaryType.B:
            if self.zero_votes:
                sentence.add("een aantal uitgebrachte stemmen van 0")
            if self.high_invalid_vote_percentage:
                sentence.add(
                    f"een hoog percentage ongeldige stemmen ({int(self.high_invalid_vote_percentage)}%)"
                )
            if self.high_blank_vote_percentage:
                sentence.add(
                    f"een hoog percentage blanco stemmen ({int(self.high_blank_vote_percentage)}%)"
                )
            if self.high_vote_difference:
                sentence.add(
                    f"een groot verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen ({self.high_vote_difference})"
                )
            if self.parties_with_high_difference_percentage:
                sentence.add(
                    f"een opmerkelijk grote afwijking ten opzichte van het gemeentegemiddelde bij de volgende partijen: {', '.join(self.parties_with_high_difference_percentage)}"
                )
            if self.potentially_switched_candidates:
                sentence.add(
                    f"een mogelijke verwisseling bij de volgende kandidaten: {', '.join((str(switch) for switch in self.potentially_switched_candidates))}"
                )

        return sentence.render(self.already_recounted)


class InvalidEmlException(Exception):
    pass
