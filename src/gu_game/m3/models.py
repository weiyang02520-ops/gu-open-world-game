"""Structured M3 information-domain records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Channel(StrEnum):
    FACE_TO_FACE = "FACE_TO_FACE"
    MARKET_GOSSIP = "MARKET_GOSSIP"
    MESSENGER = "MESSENGER"
    LOCAL_NETWORK = "LOCAL_NETWORK"


class ReportIntention(StrEnum):
    INFORM = "INFORM"
    WARN = "WARN"
    PERSUADE = "PERSUADE"
    DECEIVE = "DECEIVE"
    FRAME = "FRAME"


class BasisType(StrEnum):
    FIRST_HAND = "FIRST_HAND"
    SECOND_HAND = "SECOND_HAND"
    DELIBERATE_LIE = "DELIBERATE_LIE"
    INFERRED = "INFERRED"


class CertaintyClass(StrEnum):
    VERY_UNLIKELY = "VERY_UNLIKELY"
    UNLIKELY = "UNLIKELY"
    POSSIBLE = "POSSIBLE"
    LIKELY = "LIKELY"
    VERY_LIKELY = "VERY_LIKELY"
    NEAR_CERTAIN = "NEAR_CERTAIN"


@dataclass
class Hypothesis:
    hypothesis_id: str
    subject_id: str
    predicate: str
    object_value: Any
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "subject_id": self.subject_id,
            "predicate": self.predicate,
            "object_value": self.object_value,
            "parameters": self.parameters,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Hypothesis":
        return cls(
            hypothesis_id=str(data["hypothesis_id"]),
            subject_id=str(data["subject_id"]),
            predicate=str(data["predicate"]),
            object_value=data.get("object_value"),
            parameters=dict(data.get("parameters", {})),
        )


@dataclass
class Observation:
    observation_id: str
    observer_id: str
    event_id: str | None
    location_id: str
    observed_at: int
    observation_type: str
    perceived_features: dict[str, Any]
    quality: int
    confidence: int
    sensory_basis: str
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "observer_id": self.observer_id,
            "event_id": self.event_id,
            "location_id": self.location_id,
            "observed_at": self.observed_at,
            "observation_type": self.observation_type,
            "perceived_features": self.perceived_features,
            "quality": self.quality,
            "confidence": self.confidence,
            "sensory_basis": self.sensory_basis,
            "evidence_ids": list(self.evidence_ids),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Observation":
        return cls(
            observation_id=str(data["observation_id"]),
            observer_id=str(data["observer_id"]),
            event_id=data.get("event_id"),
            location_id=str(data["location_id"]),
            observed_at=int(data["observed_at"]),
            observation_type=str(data["observation_type"]),
            perceived_features=dict(data.get("perceived_features", {})),
            quality=int(data["quality"]),
            confidence=int(data["confidence"]),
            sensory_basis=str(data["sensory_basis"]),
            evidence_ids=[str(item) for item in data.get("evidence_ids", [])],
        )


@dataclass
class EvidenceSupport:
    evidence_id: str
    hypothesis_id: str
    support_strength: int
    contradiction_strength: int
    evaluator_context: str = "M3_RULE_ENGINE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "hypothesis_id": self.hypothesis_id,
            "support_strength": self.support_strength,
            "contradiction_strength": self.contradiction_strength,
            "evaluator_context": self.evaluator_context,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceSupport":
        return cls(
            evidence_id=str(data["evidence_id"]),
            hypothesis_id=str(data["hypothesis_id"]),
            support_strength=int(data["support_strength"]),
            contradiction_strength=int(data["contradiction_strength"]),
            evaluator_context=str(data.get("evaluator_context", "M3_RULE_ENGINE")),
        )


@dataclass
class EvidenceItem:
    evidence_id: str
    evidence_type: str
    origin_event_id: str | None
    origin_observation_id: str | None
    location_id: str
    holder_id: str | None
    created_at: int
    quality: int
    authenticity: int
    tampered: bool
    independence_group_id: str
    supports: list[EvidenceSupport] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "origin_event_id": self.origin_event_id,
            "origin_observation_id": self.origin_observation_id,
            "location_id": self.location_id,
            "holder_id": self.holder_id,
            "created_at": self.created_at,
            "quality": self.quality,
            "authenticity": self.authenticity,
            "tampered": self.tampered,
            "independence_group_id": self.independence_group_id,
            "supports": [item.to_dict() for item in self.supports],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceItem":
        return cls(
            evidence_id=str(data["evidence_id"]),
            evidence_type=str(data["evidence_type"]),
            origin_event_id=data.get("origin_event_id"),
            origin_observation_id=data.get("origin_observation_id"),
            location_id=str(data["location_id"]),
            holder_id=data.get("holder_id"),
            created_at=int(data["created_at"]),
            quality=int(data["quality"]),
            authenticity=int(data["authenticity"]),
            tampered=bool(data.get("tampered", False)),
            independence_group_id=str(data["independence_group_id"]),
            supports=[EvidenceSupport.from_dict(item) for item in data.get("supports", [])],
        )


@dataclass
class ReportClaim:
    hypothesis_id: str
    asserted_value: Any
    supports: bool
    asserted_confidence: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "asserted_value": self.asserted_value,
            "supports": self.supports,
            "asserted_confidence": self.asserted_confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReportClaim":
        return cls(
            hypothesis_id=str(data["hypothesis_id"]),
            asserted_value=data.get("asserted_value"),
            supports=bool(data["supports"]),
            asserted_confidence=int(data["asserted_confidence"]),
        )


@dataclass
class InformationReport:
    report_id: str
    sender_id: str
    receiver_id: str | None
    audience: list[str]
    created_at: int
    source_type: Channel
    claims: list[ReportClaim]
    claimed_basis: BasisType
    actual_basis: BasisType
    asserted_confidence: int
    evidence_references: list[str]
    intention: ReportIntention
    transmission_quality: int
    parent_report_id: str | None
    origin_chain_id: str
    independence_group_id: str
    delivered: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "audience": list(self.audience),
            "created_at": self.created_at,
            "source_type": self.source_type.value,
            "claims": [item.to_dict() for item in self.claims],
            "claimed_basis": self.claimed_basis.value,
            "actual_basis": self.actual_basis.value,
            "asserted_confidence": self.asserted_confidence,
            "evidence_references": list(self.evidence_references),
            "intention": self.intention.value,
            "transmission_quality": self.transmission_quality,
            "parent_report_id": self.parent_report_id,
            "origin_chain_id": self.origin_chain_id,
            "independence_group_id": self.independence_group_id,
            "delivered": sorted(self.delivered),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InformationReport":
        return cls(
            report_id=str(data["report_id"]),
            sender_id=str(data["sender_id"]),
            receiver_id=data.get("receiver_id"),
            audience=[str(item) for item in data.get("audience", [])],
            created_at=int(data["created_at"]),
            source_type=Channel(data["source_type"]),
            claims=[ReportClaim.from_dict(item) for item in data.get("claims", [])],
            claimed_basis=BasisType(data["claimed_basis"]),
            actual_basis=BasisType(data["actual_basis"]),
            asserted_confidence=int(data["asserted_confidence"]),
            evidence_references=[str(item) for item in data.get("evidence_references", [])],
            intention=ReportIntention(data["intention"]),
            transmission_quality=int(data["transmission_quality"]),
            parent_report_id=data.get("parent_report_id"),
            origin_chain_id=str(data["origin_chain_id"]),
            independence_group_id=str(data["independence_group_id"]),
            delivered=set(data.get("delivered", [])),
        )


@dataclass
class SourceProfile:
    evaluator_id: str
    source_id: str
    trustworthiness: int = 50
    domain_expertise: int = 50
    honesty_history: int = 50
    relationship_bias: int = 0
    motive_modifier: int = 0
    last_updated: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceProfile":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class BeliefRecord:
    hypothesis_id: str
    confidence: int = 50
    supporting_evidence_ids: list[str] = field(default_factory=list)
    contradicting_evidence_ids: list[str] = field(default_factory=list)
    report_ids: list[str] = field(default_factory=list)
    origin_groups_seen: list[str] = field(default_factory=list)
    last_updated: int = 0
    certainty_class: CertaintyClass = CertaintyClass.POSSIBLE
    category: str = "RUMOR"

    def refresh_class(self) -> None:
        if self.confidence >= 90:
            self.certainty_class = CertaintyClass.NEAR_CERTAIN
        elif self.confidence >= 75:
            self.certainty_class = CertaintyClass.VERY_LIKELY
        elif self.confidence >= 60:
            self.certainty_class = CertaintyClass.LIKELY
        elif self.confidence >= 40:
            self.certainty_class = CertaintyClass.POSSIBLE
        elif self.confidence >= 20:
            self.certainty_class = CertaintyClass.UNLIKELY
        else:
            self.certainty_class = CertaintyClass.VERY_UNLIKELY

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "confidence": self.confidence,
            "supporting_evidence_ids": list(self.supporting_evidence_ids),
            "contradicting_evidence_ids": list(self.contradicting_evidence_ids),
            "report_ids": list(self.report_ids),
            "origin_groups_seen": list(self.origin_groups_seen),
            "last_updated": self.last_updated,
            "certainty_class": self.certainty_class.value,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BeliefRecord":
        return cls(
            hypothesis_id=str(data["hypothesis_id"]),
            confidence=int(data.get("confidence", 50)),
            supporting_evidence_ids=[str(item) for item in data.get("supporting_evidence_ids", [])],
            contradicting_evidence_ids=[str(item) for item in data.get("contradicting_evidence_ids", [])],
            report_ids=[str(item) for item in data.get("report_ids", [])],
            origin_groups_seen=[str(item) for item in data.get("origin_groups_seen", [])],
            last_updated=int(data.get("last_updated", 0)),
            certainty_class=CertaintyClass(data.get("certainty_class", CertaintyClass.POSSIBLE.value)),
            category=str(data.get("category", "RUMOR")),
        )


@dataclass
class MemoryRecord:
    memory_id: str
    character_id: str
    event_id: str | None
    observation_id: str | None
    report_id: str | None
    memory_type: str
    salience: int
    emotional_tags: list[str]
    created_at: int
    last_recalled: int
    persistence: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryRecord":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class RelationshipState:
    source_id: str
    target_id: str
    trust: int = 50
    fear: int = 0
    respect: int = 0
    resentment: int = 0
    favor: int = 0
    last_updated: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelationshipState":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class RumorThread:
    rumor_id: str
    primary_hypothesis_id: str
    origin_report_id: str
    origin_chain_id: str
    created_at: int
    origin_location_id: str
    current_locations: list[str]
    spread_strength: int
    mutation_level: int
    public_visibility: int
    active: bool = True
    semantic_slots: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RumorThread":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class Transmission:
    transmission_id: str
    report_id: str
    receiver_id: str
    deliver_at: int
    channel: Channel
    mutation_level: int
    sequence: int

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["channel"] = self.channel.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Transmission":
        return cls(**{**data, "channel": Channel(data["channel"])})


@dataclass(frozen=True)
class InformationDecision:
    actor_id: str
    target_id: str
    action: str
    reason: str
    confidence: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
