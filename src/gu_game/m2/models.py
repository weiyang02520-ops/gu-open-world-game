"""Serializable combat domain records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from .balance import GAME_EXTENSION_COMBAT_BALANCE as B


class BodyPart(StrEnum):
    HEAD = "HEAD"
    TORSO = "TORSO"
    LEFT_ARM = "LEFT_ARM"
    RIGHT_ARM = "RIGHT_ARM"
    LEFT_LEG = "LEFT_LEG"
    RIGHT_LEG = "RIGHT_LEG"


class InjurySeverity(StrEnum):
    LIGHT = "LIGHT"
    HEAVY = "HEAVY"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class CombatStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISENGAGED = "DISENGAGED"
    INCAPACITATED_END = "INCAPACITATED_END"
    DEATH_END = "DEATH_END"


class CombatActionType(StrEnum):
    ACTIVATE_ATTACK_GU = "ACTIVATE_ATTACK_GU"
    ACTIVATE_PERCEPTION_GU = "ACTIVATE_PERCEPTION_GU"
    USE_MOVEMENT_GU = "USE_MOVEMENT_GU"
    FLEE = "FLEE"
    HOLD = "HOLD"


class CombatGuRole(StrEnum):
    ATTACK = "ATTACK"
    MOVEMENT = "MOVEMENT"
    PERCEPTION = "PERCEPTION"


@dataclass
class Injury:
    part: BodyPart
    severity: InjurySeverity
    integrity_remaining: int
    bleeding: int
    impairment: int
    incapacitating: bool = False
    fatal: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "part": self.part.value,
            "severity": self.severity.value,
            "integrity_remaining": self.integrity_remaining,
            "bleeding": self.bleeding,
            "impairment": self.impairment,
            "incapacitating": self.incapacitating,
            "fatal": self.fatal,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Injury":
        return cls(
            part=BodyPart(data["part"]),
            severity=InjurySeverity(data["severity"]),
            integrity_remaining=int(data["integrity_remaining"]),
            bleeding=int(data["bleeding"]),
            impairment=int(data["impairment"]),
            incapacitating=bool(data.get("incapacitating", False)),
            fatal=bool(data.get("fatal", False)),
        )


@dataclass
class BodyState:
    injuries: dict[BodyPart, Injury] = field(default_factory=dict)
    blood_loss: int = 0
    incapacitated: bool = False
    dead: bool = False

    def apply_hit(self, part: BodyPart, power: int) -> Injury:
        existing = self.injuries.get(part)
        remaining = (existing.integrity_remaining if existing else 100) - power
        if power >= B["critical_injury_threshold"] or remaining <= B["fatal_integrity_threshold"]:
            severity = InjurySeverity.FATAL if part in {BodyPart.HEAD, BodyPart.TORSO} else InjurySeverity.CRITICAL
        elif power >= B["heavy_injury_threshold"]:
            severity = InjurySeverity.HEAVY
        else:
            severity = InjurySeverity.LIGHT
        impairment = min(100, (existing.impairment if existing else 0) + power)
        bleeding = min(100, (existing.bleeding if existing else 0) + max(1, power // 2))
        fatal = severity is InjurySeverity.FATAL
        incapacitating = fatal or (
            part in {BodyPart.HEAD, BodyPart.TORSO} and impairment >= B["critical_injury_threshold"]
        )
        injury = Injury(
            part=part,
            severity=severity,
            integrity_remaining=max(0, remaining),
            bleeding=bleeding,
            impairment=impairment,
            incapacitating=incapacitating,
            fatal=fatal,
        )
        self.injuries[part] = injury
        self.blood_loss = min(100, self.blood_loss + bleeding)
        if fatal:
            self.dead = True
        elif incapacitating:
            self.incapacitated = True
        return injury

    def movement_distance(self, base_distance: int) -> int:
        if self.dead or self.incapacitated:
            return 0
        leg_impairment = sum(
            self.injuries.get(part, Injury(part, InjurySeverity.LIGHT, 100, 0, 0)).impairment
            for part in (BodyPart.LEFT_LEG, BodyPart.RIGHT_LEG)
        )
        return max(1, base_distance - leg_impairment // 25)

    def can_act(self) -> bool:
        return not self.dead and not self.incapacitated

    def tick_bleeding(self) -> int:
        bleeding = sum(injury.bleeding for injury in self.injuries.values())
        if bleeding <= 0:
            return 0
        before = self.blood_loss
        self.blood_loss = min(100, self.blood_loss + max(1, bleeding // 10))
        if self.blood_loss >= 100:
            self.incapacitated = True
        return self.blood_loss - before

    def summary(self) -> dict[str, Any]:
        return {
            "injuries": [self.injuries[part].to_dict() for part in sorted(self.injuries, key=lambda item: item.value)],
            "blood_loss": self.blood_loss,
            "incapacitated": self.incapacitated,
            "dead": self.dead,
            "movement_distance": self.movement_distance(B["movement_distance"]),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "injuries": {part.value: injury.to_dict() for part, injury in self.injuries.items()},
            "blood_loss": self.blood_loss,
            "incapacitated": self.incapacitated,
            "dead": self.dead,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BodyState":
        return cls(
            injuries={
                BodyPart(key): Injury.from_dict(value)
                for key, value in data.get("injuries", {}).items()
            },
            blood_loss=int(data.get("blood_loss", 0)),
            incapacitated=bool(data.get("incapacitated", False)),
            dead=bool(data.get("dead", False)),
        )


@dataclass
class CombatGuProfile:
    profile_id: str
    gu_instance_id: str
    role: CombatGuRole
    essence_cost: int
    preparation_ticks: int
    range: int = 0
    effect_power: int = 0
    perceptibility: int = 0
    movement_distance: int = 0
    perception_strength: int = 0
    target_part: BodyPart = BodyPart.LEFT_LEG
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "gu_instance_id": self.gu_instance_id,
            "role": self.role.value,
            "essence_cost": self.essence_cost,
            "preparation_ticks": self.preparation_ticks,
            "range": self.range,
            "effect_power": self.effect_power,
            "perceptibility": self.perceptibility,
            "movement_distance": self.movement_distance,
            "perception_strength": self.perception_strength,
            "target_part": self.target_part.value,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CombatGuProfile":
        return cls(
            profile_id=str(data["profile_id"]),
            gu_instance_id=str(data["gu_instance_id"]),
            role=CombatGuRole(data["role"]),
            essence_cost=int(data["essence_cost"]),
            preparation_ticks=int(data["preparation_ticks"]),
            range=int(data.get("range", 0)),
            effect_power=int(data.get("effect_power", 0)),
            perceptibility=int(data.get("perceptibility", 0)),
            movement_distance=int(data.get("movement_distance", 0)),
            perception_strength=int(data.get("perception_strength", 0)),
            target_part=BodyPart(data.get("target_part", BodyPart.LEFT_LEG.value)),
            provenance=str(data.get("provenance", "GAME_EXTENSION")),
        )


@dataclass
class CombatActorState:
    actor_id: str
    position: int
    body: BodyState = field(default_factory=BodyState)
    perception_ready: bool = False
    perception_profile_id: str | None = None
    escaped: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "position": self.position,
            "body": self.body.to_dict(),
            "perception_ready": self.perception_ready,
            "perception_profile_id": self.perception_profile_id,
            "escaped": self.escaped,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CombatActorState":
        return cls(
            actor_id=str(data["actor_id"]),
            position=int(data["position"]),
            body=BodyState.from_dict(data.get("body", {})),
            perception_ready=bool(data.get("perception_ready", False)),
            perception_profile_id=data.get("perception_profile_id"),
            escaped=bool(data.get("escaped", False)),
        )


@dataclass
class CombatAction:
    action_id: str
    action_type: CombatActionType
    actor_id: str
    target_id: str | None
    profile_id: str | None
    declared_at_ms: int
    execute_at_ms: int
    sequence: int
    accepted: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "profile_id": self.profile_id,
            "declared_at_ms": self.declared_at_ms,
            "execute_at_ms": self.execute_at_ms,
            "sequence": self.sequence,
            "accepted": self.accepted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CombatAction":
        return cls(
            action_id=str(data["action_id"]),
            action_type=CombatActionType(data["action_type"]),
            actor_id=str(data["actor_id"]),
            target_id=data.get("target_id"),
            profile_id=data.get("profile_id"),
            declared_at_ms=int(data["declared_at_ms"]),
            execute_at_ms=int(data["execute_at_ms"]),
            sequence=int(data["sequence"]),
            accepted=bool(data.get("accepted", True)),
        )


@dataclass
class ReactionWindow:
    attack_action_id: str
    defender_id: str
    opened_at_ms: int
    deadline_ms: int
    detected: bool
    selected_action_id: str | None = None
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "attack_action_id": self.attack_action_id,
            "defender_id": self.defender_id,
            "opened_at_ms": self.opened_at_ms,
            "deadline_ms": self.deadline_ms,
            "detected": self.detected,
            "selected_action_id": self.selected_action_id,
            "resolved": self.resolved,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReactionWindow":
        return cls(
            attack_action_id=str(data["attack_action_id"]),
            defender_id=str(data["defender_id"]),
            opened_at_ms=int(data["opened_at_ms"]),
            deadline_ms=int(data["deadline_ms"]),
            detected=bool(data["detected"]),
            selected_action_id=data.get("selected_action_id"),
            resolved=bool(data.get("resolved", False)),
        )


@dataclass
class CombatEncounter:
    encounter_id: str
    location_id: str
    participants: tuple[str, ...]
    combat_time_ms: int
    tick_ms: int
    actors: dict[str, CombatActorState]
    pending_actions: list[CombatAction] = field(default_factory=list)
    reaction_windows: dict[str, ReactionWindow] = field(default_factory=dict)
    resolved_action_ids: list[str] = field(default_factory=list)
    status: CombatStatus = CombatStatus.ACTIVE
    exit_reason: str | None = None
    world_clock_base_seconds: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "encounter_id": self.encounter_id,
            "location_id": self.location_id,
            "participants": list(self.participants),
            "combat_time_ms": self.combat_time_ms,
            "tick_ms": self.tick_ms,
            "actors": {key: value.to_dict() for key, value in self.actors.items()},
            "pending_actions": [item.to_dict() for item in self.pending_actions],
            "reaction_windows": {key: value.to_dict() for key, value in self.reaction_windows.items()},
            "resolved_action_ids": list(self.resolved_action_ids),
            "status": self.status.value,
            "exit_reason": self.exit_reason,
            "world_clock_base_seconds": self.world_clock_base_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CombatEncounter":
        return cls(
            encounter_id=str(data["encounter_id"]),
            location_id=str(data["location_id"]),
            participants=tuple(data.get("participants", [])),
            combat_time_ms=int(data["combat_time_ms"]),
            tick_ms=int(data.get("tick_ms", B["combat_tick_ms"])),
            actors={key: CombatActorState.from_dict(value) for key, value in data.get("actors", {}).items()},
            pending_actions=[CombatAction.from_dict(item) for item in data.get("pending_actions", [])],
            reaction_windows={
                key: ReactionWindow.from_dict(value)
                for key, value in data.get("reaction_windows", {}).items()
            },
            resolved_action_ids=[str(item) for item in data.get("resolved_action_ids", [])],
            status=CombatStatus(data.get("status", CombatStatus.ACTIVE.value)),
            exit_reason=data.get("exit_reason"),
            world_clock_base_seconds=int(data.get("world_clock_base_seconds", 0)),
        )


@dataclass(frozen=True)
class PerceivedCombatSnapshot:
    observer_id: str
    target_id: str
    distance: int
    target_visible: bool
    incoming_threat: bool
    threat_strength: int
    target_movement_impairment: int
    escape_feasible: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "observer_id": self.observer_id,
            "target_id": self.target_id,
            "distance": self.distance,
            "target_visible": self.target_visible,
            "incoming_threat": self.incoming_threat,
            "threat_strength": self.threat_strength,
            "target_movement_impairment": self.target_movement_impairment,
            "escape_feasible": self.escape_feasible,
        }


@dataclass(frozen=True)
class CombatDecision:
    actor_id: str
    decision: CombatActionType
    reason: str
    snapshot: PerceivedCombatSnapshot
