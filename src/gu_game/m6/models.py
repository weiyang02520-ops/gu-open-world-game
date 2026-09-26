"""Serializable M6 cultivation, breakthrough and attainment records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MinorStage(StrEnum):
    INITIAL = "INITIAL"
    MIDDLE = "MIDDLE"
    UPPER = "UPPER"
    PEAK = "PEAK"


class BreakthroughMode(StrEnum):
    SAFE = "SAFE"
    SUPPORTED = "SUPPORTED"
    FORCED = "FORCED"


class AttainmentRealm(StrEnum):
    ORDINARY = "ORDINARY"
    QUASI_MASTER = "QUASI_MASTER"
    MASTER = "MASTER"


class InsightType(StrEnum):
    COMBAT = "COMBAT"
    STUDY = "STUDY"
    INHERITANCE = "INHERITANCE"
    EXPERIMENTATION = "EXPERIMENTATION"
    OBSERVATION = "OBSERVATION"
    REFINEMENT = "REFINEMENT"


@dataclass
class CultivationMethod:
    method_id: str
    name: str
    progress_per_hour: int
    essence_cost_per_hour: int
    fatigue_per_hour: int
    minimum_rank: int = 1
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CultivationMethod":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class CultivationProfile:
    character_id: str
    fatigue: int = 0
    instability: int = 0
    health_modifier: int = 100
    breakthrough_ready: bool = False
    active_method_id: str = "method-breath-cycle"
    last_session_at: int = 0
    safe_breakthroughs: int = 0
    forced_attempts: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CultivationProfile":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class PathDefinition:
    path_id: str
    name: str
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PathDefinition":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class PathAttainmentState:
    character_id: str
    path_id: str
    insight_points: int = 0
    realm: AttainmentRealm = AttainmentRealm.ORDINARY
    novelty_history: dict[str, int] = field(default_factory=dict)

    def refresh_realm(self) -> None:
        if self.insight_points >= 180:
            self.realm = AttainmentRealm.MASTER
        elif self.insight_points >= 80:
            self.realm = AttainmentRealm.QUASI_MASTER
        else:
            self.realm = AttainmentRealm.ORDINARY

    def to_dict(self) -> dict[str, Any]:
        return {
            "character_id": self.character_id,
            "path_id": self.path_id,
            "insight_points": self.insight_points,
            "realm": self.realm.value,
            "novelty_history": dict(self.novelty_history),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PathAttainmentState":
        return cls(
            character_id=str(data["character_id"]),
            path_id=str(data["path_id"]),
            insight_points=int(data.get("insight_points", 0)),
            realm=AttainmentRealm(data.get("realm", AttainmentRealm.ORDINARY.value)),
            novelty_history={str(k): int(v) for k, v in data.get("novelty_history", {}).items()},
        )


@dataclass
class InsightEvent:
    insight_id: str
    character_id: str
    path_id: str
    insight_type: InsightType
    source_key: str
    base_value: int
    awarded_value: int
    novelty_factor: int
    created_at: int

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["insight_type"] = self.insight_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InsightEvent":
        return cls(**{**data, "insight_type": InsightType(data["insight_type"])})


@dataclass
class KnowledgeRecord:
    knowledge_id: str
    character_id: str
    knowledge_type: str
    subject_id: str
    learned_at: int
    source_id: str
    proficiency: int = 1

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeRecord":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class StudySource:
    source_id: str
    name: str
    location_id: str
    path_id: str
    knowledge_subject_id: str
    base_insight: int
    study_hours: int
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StudySource":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass(frozen=True)
class BreakthroughResult:
    character_id: str
    mode: BreakthroughMode
    success: bool
    stage_before: MinorStage
    stage_after: MinorStage
    roll: int | None
    target: int | None
    consequence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "character_id": self.character_id,
            "mode": self.mode.value,
            "success": self.success,
            "stage_before": self.stage_before.value,
            "stage_after": self.stage_after.value,
            "roll": self.roll,
            "target": self.target,
            "consequence": self.consequence,
        }
