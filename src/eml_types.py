from dataclasses import dataclass
from typing import Dict, Optional, Union


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
        return f"{self.value}%"


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
            f"Mogelijke verwisseling op lijst {self.candidate_with_more.party.id}{party_name}. "
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


class InvalidEmlException(Exception):
    pass
