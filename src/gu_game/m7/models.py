"""Serializable M7 effect-graph and killer-move records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ..m6.models import AttainmentRealm


class EffectNodeType(StrEnum):
    CHECK_RANGE = "CHECK_RANGE"
    DELAY = "DELAY"
    DETECT = "DETECT"
    MOVE = "MOVE"
    APPLY_INJURY = "APPLY_INJURY"
    APPLY_STATUS = "APPLY_STATUS"
    END = "END"


class KillerMoveMastery(StrEnum):
    UNSTABLE = "UNSTABLE"
    DISCOVERED = "DISCOVERED"
    USABLE = "USABLE"
    PROFICIENT = "PROFICIENT"
    MASTERED = "MASTERED"


@dataclass
class EffectNode:
    node_id: str
    node_type: EffectNodeType
    parameters: dict[str, Any] = field(default_factory=dict)
    next_node_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "parameters": dict(self.parameters),
            "next_node_id": self.next_node_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EffectNode":
        return cls(
            node_id=str(data["node_id"]),
            node_type=EffectNodeType(data["node_type"]),
            parameters=dict(data.get("parameters", {})),
            next_node_id=data.get("next_node_id"),
        )


@dataclass
class EffectGraph:
    graph_id: str
    entry_node_id: str
    nodes: dict[str, EffectNode]
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "entry_node_id": self.entry_node_id,
            "nodes": {key: value.to_dict() for key, value in sorted(self.nodes.items())},
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EffectGraph":
        return cls(
            graph_id=str(data["graph_id"]),
            entry_node_id=str(data["entry_node_id"]),
            nodes={key: EffectNode.from_dict(value) for key, value in data.get("nodes", {}).items()},
            provenance=str(data.get("provenance", "GAME_EXTENSION")),
        )


@dataclass
class KillerMoveDefinition:
    killer_move_id: str
    name: str
    creator_id: str
    core_gu_ids: list[str]
    auxiliary_gu_ids: list[str]
    path_id: str
    activation_order: list[str]
    graph_id: str
    essence_cost: int
    preparation_ms: int
    stability: int
    complexity: int
    minimum_attainment: AttainmentRealm
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["minimum_attainment"] = self.minimum_attainment.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KillerMoveDefinition":
        return cls(**{**data, "minimum_attainment": AttainmentRealm(data["minimum_attainment"])})


@dataclass
class KillerMoveInstance:
    instance_id: str
    definition_id: str
    owner_id: str
    mastery: KillerMoveMastery
    stability_modifier: int = 0
    research_count: int = 0
    last_test_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["mastery"] = self.mastery.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KillerMoveInstance":
        return cls(**{**data, "mastery": KillerMoveMastery(data["mastery"])})


@dataclass(frozen=True)
class EffectExecutionResult:
    success: bool
    killer_move_instance_id: str
    executed_nodes: tuple[str, ...]
    essence_spent: int
    outcome: str
    backlash: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "killer_move_instance_id": self.killer_move_instance_id,
            "executed_nodes": list(self.executed_nodes),
            "essence_spent": self.essence_spent,
            "outcome": self.outcome,
            "backlash": self.backlash,
        }
