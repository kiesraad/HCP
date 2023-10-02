from dataclasses import dataclass
from typing import Optional, Dict


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


@dataclass
class ReportingUnitInfo:
    reporting_unit_id: Optional[str]
    reporting_unit_name: Optional[str]
    cast: int
    total_counted: int
    rejected_votes: Dict[str, int]
    uncounted_votes: Dict[str, int]
    votes_per_party: Dict[str, int]


class InvalidEmlException(Exception):
    pass
