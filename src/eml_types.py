from dataclasses import dataclass
from typing import Optional, Dict, Union


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
    reporting_unit_names: Dict[Optional[str], Optional[str]]


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


class InvalidEmlException(Exception):
    pass
