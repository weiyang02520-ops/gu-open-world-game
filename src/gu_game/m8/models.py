"""Serializable M8 integrated-world records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SimulationLevel(StrEnum):
    ACTIVE = "ACTIVE"
    NEAR = "NEAR"
    REGIONAL = "REGIONAL"
    ABSTRACT = "ABSTRACT"


class StrategyProfile(StrEnum):
    COOPERATIVE = "cooperative"
    ADVERSARIAL = "adversarial"


class CanonAnchorStatus(StrEnum):
    PENDING = "PENDING"
    ELIGIBLE = "ELIGIBLE"
    DIVERGED = "DIVERGED"
    RESOLVED = "RESOLVED"


@dataclass
class LocationNode:
    location_id: str
    name: str
    kind: str
    parent_id: str | None
    neighbors: dict[str, int] = field(default_factory=dict)
    level: SimulationLevel = SimulationLevel.ABSTRACT
    hidden: bool = False
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["level"] = self.level.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocationNode":
        return cls(**{**data, "level": SimulationLevel(data.get("level", SimulationLevel.ABSTRACT.value))})


@dataclass
class ImportantNpcProfile:
    character_id: str
    role: str
    faction_id: str | None
    home_location_id: str
    goal_tags: list[str]
    importance: int = 50

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImportantNpcProfile":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class RemoteActorState:
    character_id: str
    location_id: str
    level: SimulationLevel
    next_action_at: int
    action_count: int = 0
    last_action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["level"] = self.level.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RemoteActorState":
        return cls(**{**data, "level": SimulationLevel(data["level"])})


@dataclass
class CanonAnchor:
    anchor_id: str
    expected_participants: list[str]
    location_id: str
    prerequisites: list[str]
    earliest_day: int
    latest_day: int
    divergence_policy: str
    provenance: str
    source_locator: str | None = None
    status: CanonAnchorStatus = CanonAnchorStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CanonAnchor":
        return cls(**{**data, "status": CanonAnchorStatus(data.get("status", CanonAnchorStatus.PENDING.value))})
