from dataclasses import dataclass
from typing import Dict, Optional, Union


@dataclass
class EmlMetadata:
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
    id: int
    name: Optional[str]


@dataclass(frozen=True, order=True)
class CandidateIdentifier:
    party: PartyIdentifier
    cand_id: int


@dataclass
class ReportingUnitInfo:
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
    value: int


@dataclass
class VoteDifferencePercentage:
    value: float


VoteDifference = Union[VoteDifferenceAmount, VoteDifferencePercentage]


@dataclass
class SwitchedCandidate:
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
    minimum_reporting_units_municipality: int
    minimum_reporting_units_neighbourhood: int
    minimum_deviation_factor: int
    minimum_votes: int


class InvalidEmlException(Exception):
    pass
