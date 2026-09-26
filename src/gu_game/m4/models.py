"""Serializable M4 institutional domain records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MembershipStatus(StrEnum):
    OUTSIDER = "OUTSIDER"
    AFFILIATE = "AFFILIATE"
    MEMBER = "MEMBER"
    INNER_MEMBER = "INNER_MEMBER"
    ELDER = "ELDER"
    SUSPENDED = "SUSPENDED"
    EXILED = "EXILED"
    TRAITOR = "TRAITOR"


class FactionCaseStatus(StrEnum):
    RUMOR = "RUMOR"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    SUSPECTED = "SUSPECTED"
    CONFIRMED = "CONFIRMED"
    DISPUTED = "DISPUTED"
    CLOSED = "CLOSED"


class FactionStandingLevel(StrEnum):
    UNKNOWN = "UNKNOWN"
    NEUTRAL = "NEUTRAL"
    TOLERATED = "TOLERATED"
    FRIENDLY = "FRIENDLY"
    GUEST = "GUEST"
    ALLY = "ALLY"
    MEMBER = "MEMBER"
    SUSPICIOUS = "SUSPICIOUS"
    WATCHED = "WATCHED"
    WANTED = "WANTED"
    HOSTILE = "HOSTILE"
    ENEMY = "ENEMY"


class FactionProposalType(StrEnum):
    OPEN_INVESTIGATION = "OPEN_INVESTIGATION"
    WATCH_SUBJECT = "WATCH_SUBJECT"
    RECRUIT_SUBJECT = "RECRUIT_SUBJECT"
    OFFER_AFFILIATION = "OFFER_AFFILIATION"
    ISSUE_MISSION = "ISSUE_MISSION"
    REWARD_SUBJECT = "REWARD_SUBJECT"
    RESTRICT_ACCESS = "RESTRICT_ACCESS"
    SANCTION_SUBJECT = "SANCTION_SUBJECT"
    CLOSE_CASE = "CLOSE_CASE"


@dataclass
class FactionDefinition:
    faction_id: str
    name: str
    faction_type: str
    headquarters_location_id: str
    governance_model: str
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionDefinition":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class FactionNeed:
    need_id: str
    faction_id: str
    need_type: str
    intensity: int
    target: str | None = None
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionNeed":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class Membership:
    character_id: str
    faction_id: str
    status: MembershipStatus = MembershipStatus.OUTSIDER
    joined_at: int = 0
    contribution: int = 0
    loyalty: int = 0
    privileges: list[str] = field(default_factory=list)
    restrictions: list[str] = field(default_factory=list)
    sponsor_id: str | None = None
    favor_balance: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Membership":
        return cls(**{**data, "status": MembershipStatus(data.get("status", MembershipStatus.OUTSIDER.value))})


@dataclass
class OfficeAssignment:
    assignment_id: str
    faction_id: str
    character_id: str
    office_type: str
    authority: list[str]
    appointed_at: int
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OfficeAssignment":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class PoliticalBloc:
    bloc_id: str
    faction_id: str
    name: str
    member_ids: list[str]
    priorities: dict[str, int]
    influence: int
    risk_tolerance: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PoliticalBloc":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class InstitutionalBelief:
    faction_id: str
    hypothesis_id: str
    confidence: int
    source_report_ids: list[str]
    origin_groups: list[str]
    updated_at: int
    official_status: str = "DISPUTED"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InstitutionalBelief":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class SocialIdentity:
    identity_id: str
    character_id: str
    alias: str
    known_by: list[str]
    is_real_identity: bool = False

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SocialIdentity":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class ReputationVector:
    audience_id: str
    identity_id: str
    trust: int = 50
    competence: int = 50
    strength: int = 50
    danger: int = 0
    reliability: int = 50
    generosity: int = 0
    ruthlessness: int = 0
    unpredictability: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReputationVector":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class FactionStanding:
    faction_id: str
    identity_id: str
    level: FactionStandingLevel
    reason: str
    updated_at: int

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["level"] = self.level.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionStanding":
        return cls(**{**data, "level": FactionStandingLevel(data["level"])})


@dataclass
class FactionCase:
    case_id: str
    faction_id: str
    subject_identity_id: str
    hypothesis_ids: list[str]
    opened_at: int
    status: FactionCaseStatus
    evidence_ids: list[str]
    report_ids: list[str]
    assigned_investigator: str | None
    institutional_confidence: int
    recommended_actions: list[str]
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionCase":
        return cls(**{**data, "status": FactionCaseStatus(data["status"])})


@dataclass
class Vote:
    voter_id: str
    bloc_id: str | None
    approve: bool
    score: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Vote":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class FactionProposal:
    proposal_id: str
    faction_id: str
    proposal_type: FactionProposalType
    proposer_id: str
    target_identity_id: str | None
    created_at: int
    rationale: list[str]
    referenced_case_id: str | None
    cost: int
    risks: int
    votes: list[Vote] = field(default_factory=list)
    status: str = "OPEN"
    resolution: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["proposal_type"] = self.proposal_type.value
        data["votes"] = [vote.to_dict() for vote in self.votes]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionProposal":
        return cls(**{**data, "proposal_type": FactionProposalType(data["proposal_type"]), "votes": [Vote.from_dict(item) for item in data.get("votes", [])]})


@dataclass
class InfluenceVector:
    character_id: str
    faction_id: str
    formal_authority: int = 0
    economic: int = 0
    information: int = 0
    prestige: int = 0
    coercive: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InfluenceVector":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class FactionMission:
    mission_id: str
    faction_id: str
    issuer_id: str
    need_type: str
    objective_type: str
    target_id: str | None
    reward: int
    deadline: int
    eligibility: list[str]
    status: str = "AVAILABLE"
    assignee_id: str | None = None
    progress: int = 0
    required_quantity: int = 1
    accepted_at: int | None = None
    completed_at: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionMission":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class FactionState:
    faction_id: str
    treasury: int
    controlled_locations: list[str]
    security_level: int
    stability: int
    cohesion: int
    prestige: int
    external_relations: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionState":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})
