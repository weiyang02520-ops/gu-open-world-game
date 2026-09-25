"""Small provenance model that keeps source certainty explicit."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Provenance(StrEnum):
    CANON_EXPLICIT = "CANON_EXPLICIT"
    FAN_COMPILED = "FAN_COMPILED"
    GAME_EXTENSION = "GAME_EXTENSION"


class EvidenceLevel(StrEnum):
    EXPLICIT = "EXPLICIT"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    locator: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.title:
            raise ValueError("source_id and title are required")

    def to_dict(self) -> dict[str, str | None]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "locator": self.locator,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Source":
        return cls(
            source_id=str(data["source_id"]),
            title=str(data["title"]),
            locator=data.get("locator"),
            note=data.get("note"),
        )


@dataclass(frozen=True)
class Claim:
    subject: str
    predicate: str
    value: Any
    provenance: Provenance
    evidence_level: EvidenceLevel = EvidenceLevel.UNKNOWN
    source: Source | None = None
    temporal_scope: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.subject or not self.predicate:
            raise ValueError("subject and predicate are required")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "value": self.value,
            "provenance": self.provenance.value,
            "evidence_level": self.evidence_level.value,
            "source": self.source.to_dict() if self.source else None,
            "temporal_scope": self.temporal_scope,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Claim":
        source_data = data.get("source")
        return cls(
            subject=str(data["subject"]),
            predicate=str(data["predicate"]),
            value=data.get("value"),
            provenance=Provenance(data["provenance"]),
            evidence_level=EvidenceLevel(data.get("evidence_level", EvidenceLevel.UNKNOWN.value)),
            source=Source.from_dict(source_data) if source_data else None,
            temporal_scope=data.get("temporal_scope"),
            confidence=data.get("confidence"),
        )
