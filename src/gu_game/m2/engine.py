"""Deterministic M2 combat engine layered on the M1 headless world."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.events import DomainEvent
from ..m1.models import Character
from ..m1.simulation import Simulation
from ..provenance import Provenance
from ..save import load_world, save_world
from .balance import GAME_EXTENSION_COMBAT_BALANCE as B
from .models import (
    BodyPart,
    CombatAction,
    CombatActionType,
    CombatActorState,
    CombatDecision,
    CombatEncounter,
    CombatGuProfile,
    CombatStatus,
    CombatGuRole,
    InjurySeverity,
    PerceivedCombatSnapshot,
    ReactionWindow,
)


class CombatValidationError(ValueError):
    """Raised when a combat intent is invalid without mutating state."""


@dataclass(frozen=True)
class CombatActionResult:
    success: bool
    action_id: str | None
    reason: str


class CombatEngine:
    """Combat state machine with integer tick ordering and M1 persistence."""

    M2_SCHEMA_VERSION = 1

    def __init__(self, simulation: Simulation) -> None:
        self.simulation = simulation
        self.world = simulation.world
        self.event_bus = simulation.event_bus
        self.profiles: dict[str, CombatGuProfile] = {}
        self.encounters: dict[str, CombatEncounter] = {}
        self.npc_risk_tolerance: dict[str, int] = {}
        self._sequence = 0

    @classmethod
    def new(cls, simulation: Simulation) -> "CombatEngine":
        engine = cls(simulation)
        engine.register_default_profiles()
        return engine

    @classmethod
    def from_simulation(cls, simulation: Simulation) -> "CombatEngine":
        engine = cls(simulation)
        data = simulation.world.game_state.get("m2_combat")
        if data:
            engine._load_dict(data)
        else:
            engine.register_default_profiles()
        return engine

    @classmethod
    def load(cls, path: str | Path) -> "CombatEngine":
        world = load_world(path)
        simulation = Simulation.from_world_state(world)
        return cls.from_simulation(simulation)

    def save(self, path: str | Path) -> Path:
        self._sync_world_state()
        return save_world(self.world, path)

    def register_default_profiles(self) -> None:
        """Expose three minimal combat roles over owned Gu instances."""

        for character_id, character in sorted(self.simulation.characters.items()):
            if not character.owned_gu_ids:
                continue
            source_ids = list(character.owned_gu_ids)
            role_sources = {
                CombatGuRole.ATTACK: source_ids[0],
                CombatGuRole.MOVEMENT: source_ids[min(1, len(source_ids) - 1)],
                CombatGuRole.PERCEPTION: source_ids[min(2, len(source_ids) - 1)],
            }
            for role, gu_id in role_sources.items():
                profile_id = f"{gu_id}::{role.value.lower()}"
                if profile_id in self.profiles:
                    continue
                if role is CombatGuRole.ATTACK:
                    profile = CombatGuProfile(
                        profile_id=profile_id,
                        gu_instance_id=gu_id,
                        role=role,
                        essence_cost=B["attack_essence_cost"],
                        preparation_ticks=B["attack_preparation_ticks"],
                        range=B["attack_range"],
                        effect_power=B["attack_power"],
                        perceptibility=B["attack_perceptibility"],
                        target_part=BodyPart.LEFT_LEG,
                    )
                elif role is CombatGuRole.MOVEMENT:
                    profile = CombatGuProfile(
                        profile_id=profile_id,
                        gu_instance_id=gu_id,
                        role=role,
                        essence_cost=B["movement_essence_cost"],
                        preparation_ticks=B["movement_preparation_ticks"],
                        movement_distance=B["movement_distance"],
                    )
                else:
                    profile = CombatGuProfile(
                        profile_id=profile_id,
                        gu_instance_id=gu_id,
                        role=role,
                        essence_cost=B["perception_essence_cost"],
                        preparation_ticks=B["perception_preparation_ticks"],
                        perception_strength=B["perception_strength"],
                    )
                self.profiles[profile_id] = profile
                if character.controller.value == "AI":
                    self.npc_risk_tolerance.setdefault(character_id, B["npc_risk_tolerance"])

    def profile_for_role(self, actor_id: str, role: CombatGuRole) -> CombatGuProfile:
        character = self._character(actor_id)
        for profile in self.profiles.values():
            if profile.gu_instance_id in character.owned_gu_ids and profile.role is role:
                return profile
        raise CombatValidationError(f"no {role.value} Gu profile for {actor_id}")

    def start_encounter(
        self,
        participants: tuple[str, ...] | list[str],
        *,
        positions: dict[str, int] | None = None,
        location_id: str = "location-southern-grove",
    ) -> CombatEncounter:
        participant_ids = tuple(participants)
        if len(participant_ids) < 2 or len(set(participant_ids)) != len(participant_ids):
            raise CombatValidationError("an encounter requires at least two unique participants")
        for actor_id in participant_ids:
            self._character(actor_id)
        if not self.profiles:
            self.register_default_profiles()
        positions = positions or {actor_id: index * 4 for index, actor_id in enumerate(participant_ids)}
        if set(positions) != set(participant_ids):
            raise CombatValidationError("positions must cover every participant")
        encounter_id = self.world.entity_ids.next("encounter")
        encounter = CombatEncounter(
            encounter_id=encounter_id,
            location_id=location_id,
            participants=participant_ids,
            combat_time_ms=0,
            tick_ms=B["combat_tick_ms"],
            actors={
                actor_id: CombatActorState(actor_id=actor_id, position=int(positions[actor_id]))
                for actor_id in participant_ids
            },
            world_clock_base_seconds=self.world.clock.elapsed_seconds,
        )
        self.encounters[encounter_id] = encounter
        self._emit(
            encounter,
            "COMBAT_STARTED",
            actor_id=None,
            payload={
                "participants": list(participant_ids),
                "tick_ms": encounter.tick_ms,
                "positions": dict(positions),
            },
        )
        self._sync_world_state()
        return encounter

    def activate_perception(self, encounter_id: str, actor_id: str, profile_id: str) -> CombatActionResult:
        encounter = self._active_encounter(encounter_id)
        profile = self._profile_for_actor(profile_id, actor_id, CombatGuRole.PERCEPTION)
        actor = encounter.actors[actor_id]
        self._require_essence(actor_id, profile.essence_cost)
        self._deduct_essence(actor_id, profile.essence_cost)
        action_id = self.world.entity_ids.next("combat-action")
        actor.perception_ready = True
        actor.perception_profile_id = profile.profile_id
        self._emit(
            encounter,
            "COMBAT_ACTION_DECLARED",
            actor_id=actor_id,
            payload={"action_id": action_id, "action_type": CombatActionType.ACTIVATE_PERCEPTION_GU.value},
        )
        self._emit(
            encounter,
            "GU_ACTIVATION_STARTED",
            actor_id=actor_id,
            target_ids=(actor_id,),
            payload={
                "action_id": action_id,
                "profile_id": profile.profile_id,
                "role": profile.role.value,
                "execute_at_ms": encounter.combat_time_ms,
                "essence_cost": profile.essence_cost,
            },
        )
        self._emit(
            encounter,
            "GU_ACTIVATED",
            actor_id=actor_id,
            target_ids=(actor_id,),
            payload={"action_id": action_id, "profile_id": profile.profile_id, "role": profile.role.value},
        )
        self._sync_world_state()
        return CombatActionResult(True, action_id, "perception_ready")

    def declare_attack(
        self,
        encounter_id: str,
        actor_id: str,
        target_id: str,
        profile_id: str,
    ) -> CombatActionResult:
        encounter = self._active_encounter(encounter_id)
        profile = self._profile_for_actor(profile_id, actor_id, CombatGuRole.ATTACK)
        self._validate_target(encounter, actor_id, target_id)
        attacker = encounter.actors[actor_id]
        target = encounter.actors[target_id]
        if not attacker.body.can_act():
            raise CombatValidationError("attacker cannot act")
        distance = abs(attacker.position - target.position)
        if distance > profile.range:
            raise CombatValidationError("target is outside attack range")
        self._require_essence(actor_id, profile.essence_cost)
        self._deduct_essence(actor_id, profile.essence_cost)
        action_id = self.world.entity_ids.next("combat-action")
        self._sequence += 1
        execute_at = encounter.combat_time_ms + profile.preparation_ticks * encounter.tick_ms
        action = CombatAction(
            action_id=action_id,
            action_type=CombatActionType.ACTIVATE_ATTACK_GU,
            actor_id=actor_id,
            target_id=target_id,
            profile_id=profile.profile_id,
            declared_at_ms=encounter.combat_time_ms,
            execute_at_ms=execute_at,
            sequence=self._sequence,
        )
        encounter.pending_actions.append(action)
        self._emit(
            encounter,
            "COMBAT_ACTION_DECLARED",
            actor_id=actor_id,
            target_ids=(target_id,),
            payload={
                "action_id": action_id,
                "action_type": action.action_type.value,
                "profile_id": profile.profile_id,
                "distance": distance,
                "execute_at_ms": execute_at,
            },
        )
        self._emit(
            encounter,
            "GU_ACTIVATION_STARTED",
            actor_id=actor_id,
            target_ids=(target_id,),
            payload={
                "action_id": action_id,
                "profile_id": profile.profile_id,
                "role": profile.role.value,
                "execute_at_ms": execute_at,
                "essence_cost": profile.essence_cost,
            },
        )
        detected = self._detect_attack(encounter, action, profile)
        encounter.reaction_windows[action_id] = ReactionWindow(
            attack_action_id=action_id,
            defender_id=target_id,
            opened_at_ms=encounter.combat_time_ms,
            deadline_ms=execute_at,
            detected=detected,
        )
        self._emit(
            encounter,
            "THREAT_PERCEIVED" if detected else "THREAT_NOT_PERCEIVED",
            actor_id=target_id,
            target_ids=(actor_id,),
            payload={
                "attack_action_id": action_id,
                "detected": detected,
                "deadline_ms": execute_at,
                "perceptibility": profile.perceptibility,
            },
        )
        self._sync_world_state()
        return CombatActionResult(True, action_id, "attack_declared")

    def select_reaction(
        self,
        encounter_id: str,
        actor_id: str,
        profile_id: str,
    ) -> CombatActionResult:
        encounter = self._active_encounter(encounter_id)
        profile = self._profile_for_actor(profile_id, actor_id, CombatGuRole.MOVEMENT)
        window = self._latest_reaction_window(encounter, actor_id)
        if window is None or not window.detected or encounter.combat_time_ms > window.deadline_ms:
            self._emit(
                encounter,
                "REACTION_SELECTED",
                actor_id=actor_id,
                payload={"accepted": False, "reason": "no_active_detected_window"},
            )
            return CombatActionResult(False, None, "no_active_detected_window")
        try:
            self._require_essence(actor_id, profile.essence_cost)
        except CombatValidationError:
            self._emit(
                encounter,
                "REACTION_SELECTED",
                actor_id=actor_id,
                payload={
                    "accepted": False,
                    "reason": "insufficient_essence",
                    "attack_action_id": window.attack_action_id,
                },
            )
            return CombatActionResult(False, None, "insufficient_essence")
        self._deduct_essence(actor_id, profile.essence_cost)
        self._sequence += 1
        action_id = self.world.entity_ids.next("combat-action")
        action = CombatAction(
            action_id=action_id,
            action_type=CombatActionType.USE_MOVEMENT_GU,
            actor_id=actor_id,
            target_id=self._attack_for_window(encounter, window).actor_id,
            profile_id=profile.profile_id,
            declared_at_ms=encounter.combat_time_ms,
            execute_at_ms=encounter.combat_time_ms + profile.preparation_ticks * encounter.tick_ms,
            sequence=self._sequence,
        )
        encounter.pending_actions.append(action)
        window.selected_action_id = action_id
        self._emit(
            encounter,
            "COMBAT_ACTION_DECLARED",
            actor_id=actor_id,
            payload={
                "action_id": action_id,
                "action_type": action.action_type.value,
                "profile_id": profile.profile_id,
                "execute_at_ms": action.execute_at_ms,
            },
        )
        self._emit(
            encounter,
            "REACTION_SELECTED",
            actor_id=actor_id,
            payload={
                "accepted": True,
                "reaction": action.action_type.value,
                "attack_action_id": window.attack_action_id,
                "action_id": action_id,
            },
        )
        self._sync_world_state()
        return CombatActionResult(True, action_id, "reaction_scheduled")

    def declare_flee(
        self,
        encounter_id: str,
        actor_id: str,
        target_id: str,
        profile_id: str,
    ) -> CombatActionResult:
        encounter = self._active_encounter(encounter_id)
        profile = self._profile_for_actor(profile_id, actor_id, CombatGuRole.MOVEMENT)
        self._validate_target(encounter, actor_id, target_id)
        if not encounter.actors[actor_id].body.can_act():
            raise CombatValidationError("actor cannot flee")
        self._require_essence(actor_id, profile.essence_cost)
        self._deduct_essence(actor_id, profile.essence_cost)
        self._sequence += 1
        action_id = self.world.entity_ids.next("combat-action")
        action = CombatAction(
            action_id=action_id,
            action_type=CombatActionType.FLEE,
            actor_id=actor_id,
            target_id=target_id,
            profile_id=profile.profile_id,
            declared_at_ms=encounter.combat_time_ms,
            execute_at_ms=encounter.combat_time_ms + profile.preparation_ticks * encounter.tick_ms,
            sequence=self._sequence,
        )
        encounter.pending_actions.append(action)
        self._emit(
            encounter,
            "FLEE_ATTEMPTED",
            actor_id=actor_id,
            target_ids=(target_id,),
            payload={"action_id": action_id, "execute_at_ms": action.execute_at_ms},
        )
        self._sync_world_state()
        return CombatActionResult(True, action_id, "flee_scheduled")

    def hold(self, encounter_id: str, actor_id: str) -> CombatActionResult:
        encounter = self._active_encounter(encounter_id)
        if actor_id not in encounter.actors:
            raise CombatValidationError("actor is not in encounter")
        action_id = self.world.entity_ids.next("combat-action")
        self._emit(
            encounter,
            "REACTION_SELECTED",
            actor_id=actor_id,
            payload={"accepted": True, "reaction": CombatActionType.HOLD.value, "action_id": action_id},
        )
        self._sync_world_state()
        return CombatActionResult(True, action_id, "hold")

    def advance_ticks(self, encounter_id: str, ticks: int = 1) -> CombatEncounter:
        encounter = self._active_encounter(encounter_id)
        if not isinstance(ticks, int) or isinstance(ticks, bool) or ticks < 0:
            raise ValueError("ticks must be a non-negative integer")
        for _ in range(ticks):
            if encounter.status is not CombatStatus.ACTIVE:
                break
            encounter.combat_time_ms += encounter.tick_ms
            self._reconcile_world_clock(encounter)
            due = sorted(
                [item for item in encounter.pending_actions if item.execute_at_ms <= encounter.combat_time_ms],
                key=lambda item: (item.execute_at_ms, item.sequence),
            )
            for action in due:
                if action in encounter.pending_actions:
                    encounter.pending_actions.remove(action)
                self._resolve_action(encounter, action)
                encounter.resolved_action_ids.append(action.action_id)
                if encounter.status is not CombatStatus.ACTIVE:
                    break
            self._tick_bleeding(encounter)
        self._sync_world_state()
        return encounter

    def perceived_snapshot(
        self, encounter_id: str, observer_id: str, target_id: str
    ) -> PerceivedCombatSnapshot:
        encounter = self._active_encounter(encounter_id)
        self._validate_target(encounter, observer_id, target_id)
        observer = encounter.actors[observer_id]
        target = encounter.actors[target_id]
        distance = abs(observer.position - target.position)
        incoming = any(
            action.action_type is CombatActionType.ACTIVATE_ATTACK_GU
            and action.target_id == observer_id
            for action in encounter.pending_actions
        )
        threat_strength = 0
        for action in encounter.pending_actions:
            if action.target_id == observer_id and action.profile_id in self.profiles:
                threat_strength = max(threat_strength, self.profiles[action.profile_id].perceptibility)
        impairment = 100 - target.body.movement_distance(B["movement_distance"]) * 10
        movement_profile = self.profile_for_role(observer_id, CombatGuRole.MOVEMENT)
        escape_feasible = observer.body.can_act() and self._character(observer_id).cultivation.primeval_current >= movement_profile.essence_cost
        return PerceivedCombatSnapshot(
            observer_id=observer_id,
            target_id=target_id,
            distance=distance,
            target_visible=distance <= B["disengage_distance"],
            incoming_threat=incoming,
            threat_strength=threat_strength,
            target_movement_impairment=max(0, impairment),
            escape_feasible=escape_feasible,
        )

    def choose_npc_action(
        self, encounter_id: str, npc_id: str, target_id: str
    ) -> CombatDecision:
        encounter = self._active_encounter(encounter_id)
        character = self._character(npc_id)
        if character.controller.value != "AI":
            raise CombatValidationError("choose_npc_action requires an AI controller")
        snapshot = self.perceived_snapshot(encounter_id, npc_id, target_id)
        own = encounter.actors[npc_id]
        attack = self.profile_for_role(npc_id, CombatGuRole.ATTACK)
        movement = self.profile_for_role(npc_id, CombatGuRole.MOVEMENT)
        tolerance = self.npc_risk_tolerance.get(npc_id, B["npc_risk_tolerance"])
        if not own.body.can_act():
            decision, reason = CombatActionType.HOLD, "own_body_unable_to_act"
        elif snapshot.incoming_threat and (
            character.cultivation.primeval_current < attack.essence_cost
            or snapshot.threat_strength > tolerance
            or not snapshot.escape_feasible
        ):
            decision, reason = CombatActionType.FLEE, "visible_risk_exceeds_tolerance"
        elif not snapshot.target_visible or snapshot.distance > attack.range:
            decision, reason = CombatActionType.HOLD, "target_not_in_visible_attack_range"
        elif character.cultivation.primeval_current >= attack.essence_cost:
            decision, reason = CombatActionType.ACTIVATE_ATTACK_GU, "visible_target_within_range"
        elif character.cultivation.primeval_current >= movement.essence_cost:
            decision, reason = CombatActionType.FLEE, "insufficient_attack_essence"
        else:
            decision, reason = CombatActionType.HOLD, "insufficient_combat_essence"
        result = CombatDecision(npc_id, decision, reason, snapshot)
        self._emit(
            encounter,
            "NPC_COMBAT_DECISION",
            actor_id=npc_id,
            target_ids=(target_id,),
            payload={"decision": decision.value, "reason": reason, "perceived": snapshot.to_dict()},
        )
        self._sync_world_state()
        return result

    def run_npc_decision(self, encounter_id: str, npc_id: str, target_id: str) -> CombatDecision:
        decision = self.choose_npc_action(encounter_id, npc_id, target_id)
        if decision.decision is CombatActionType.ACTIVATE_ATTACK_GU:
            self.declare_attack(
                encounter_id,
                npc_id,
                target_id,
                self.profile_for_role(npc_id, CombatGuRole.ATTACK).profile_id,
            )
        elif decision.decision is CombatActionType.FLEE:
            self.declare_flee(
                encounter_id,
                npc_id,
                target_id,
                self.profile_for_role(npc_id, CombatGuRole.MOVEMENT).profile_id,
            )
        else:
            self.hold(encounter_id, npc_id)
        return decision

    def summary(self, encounter_id: str) -> dict[str, Any]:
        encounter = self.encounters[encounter_id]
        return {
            "encounter_id": encounter.encounter_id,
            "status": encounter.status.value,
            "exit_reason": encounter.exit_reason,
            "combat_time_ms": encounter.combat_time_ms,
            "tick_ms": encounter.tick_ms,
            "positions": {actor_id: state.position for actor_id, state in encounter.actors.items()},
            "actors": {actor_id: state.body.summary() for actor_id, state in encounter.actors.items()},
            "pending_actions": len(encounter.pending_actions),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "m2_schema_version": self.M2_SCHEMA_VERSION,
            "profiles": {key: value.to_dict() for key, value in sorted(self.profiles.items())},
            "encounters": {key: value.to_dict() for key, value in sorted(self.encounters.items())},
            "npc_risk_tolerance": dict(self.npc_risk_tolerance),
            "sequence": self._sequence,
        }

    def _load_dict(self, data: dict[str, Any]) -> None:
        self.profiles = {
            key: CombatGuProfile.from_dict(value) for key, value in data.get("profiles", {}).items()
        }
        self.encounters = {
            key: CombatEncounter.from_dict(value) for key, value in data.get("encounters", {}).items()
        }
        self.npc_risk_tolerance = {
            str(key): int(value) for key, value in data.get("npc_risk_tolerance", {}).items()
        }
        self._sequence = int(data.get("sequence", 0))
        if not self.profiles:
            self.register_default_profiles()

    def _sync_world_state(self) -> None:
        self.simulation._sync_world_state()
        self.world.game_state["m2_combat"] = self.to_dict()

    def _resolve_action(self, encounter: CombatEncounter, action: CombatAction) -> None:
        if action.action_type is CombatActionType.ACTIVATE_ATTACK_GU:
            self._resolve_attack(encounter, action)
        elif action.action_type is CombatActionType.USE_MOVEMENT_GU:
            self._resolve_movement(encounter, action, fleeing=False)
        elif action.action_type is CombatActionType.FLEE:
            self._resolve_movement(encounter, action, fleeing=True)

    def _resolve_attack(self, encounter: CombatEncounter, action: CombatAction) -> None:
        profile = self.profiles[action.profile_id or ""]
        target_id = action.target_id
        if target_id is None or target_id not in encounter.actors:
            return
        attacker = encounter.actors[action.actor_id]
        target = encounter.actors[target_id]
        window = encounter.reaction_windows.get(action.action_id)
        self._emit(
            encounter,
            "GU_ACTIVATED",
            actor_id=action.actor_id,
            target_ids=(target_id,),
            payload={
                "action_id": action.action_id,
                "profile_id": profile.profile_id,
                "role": profile.role.value,
                "combat_time_ms": encounter.combat_time_ms,
            },
        )
        if target.escaped or target.body.dead:
            self._emit(
                encounter,
                "ATTACK_MISSED",
                actor_id=action.actor_id,
                target_ids=(target_id,),
                payload={"reason": "target_exited", "action_id": action.action_id},
            )
            return
        distance = abs(attacker.position - target.position)
        reacted = bool(window and window.selected_action_id in encounter.resolved_action_ids)
        if reacted and distance > profile.range:
            if window:
                window.resolved = True
            self._emit(
                encounter,
                "ATTACK_EVADED",
                actor_id=action.actor_id,
                target_ids=(target_id,),
                payload={"action_id": action.action_id, "distance_after_reaction": distance},
            )
            return
        if distance > profile.range:
            self._emit(
                encounter,
                "ATTACK_MISSED",
                actor_id=action.actor_id,
                target_ids=(target_id,),
                payload={"reason": "out_of_range_at_resolution", "distance": distance},
            )
            return
        self._emit(
            encounter,
            "ATTACK_HIT",
            actor_id=action.actor_id,
            target_ids=(target_id,),
            payload={"action_id": action.action_id, "distance": distance, "body_part": profile.target_part.value},
        )
        injury = target.body.apply_hit(profile.target_part, profile.effect_power)
        self._emit(
            encounter,
            "INJURY_APPLIED",
            actor_id=action.actor_id,
            target_ids=(target_id,),
            payload={
                "action_id": action.action_id,
                "body_part": injury.part.value,
                "severity": injury.severity.value,
                "bleeding": injury.bleeding,
                "impairment": injury.impairment,
                "integrity_remaining": injury.integrity_remaining,
                "incapacitating": injury.incapacitating,
                "fatal": injury.fatal,
            },
        )
        if injury.fatal:
            self._end_encounter(encounter, CombatStatus.DEATH_END, "fatal_injury", target_id)
        elif injury.incapacitating:
            self._end_encounter(encounter, CombatStatus.INCAPACITATED_END, "incapacitating_injury", target_id)

    def _resolve_movement(self, encounter: CombatEncounter, action: CombatAction, *, fleeing: bool) -> None:
        profile = self.profiles[action.profile_id or ""]
        actor = encounter.actors[action.actor_id]
        target_id = action.target_id
        if target_id is None or target_id not in encounter.actors:
            return
        target = encounter.actors[target_id]
        if not actor.body.can_act():
            return
        distance = actor.body.movement_distance(profile.movement_distance)
        if fleeing:
            distance *= B["flee_distance_multiplier"]
        direction = 1 if actor.position >= target.position else -1
        actor.position += direction * distance
        self._emit(
            encounter,
            "GU_ACTIVATED",
            actor_id=action.actor_id,
            target_ids=(target_id,),
            payload={
                "action_id": action.action_id,
                "profile_id": profile.profile_id,
                "role": profile.role.value,
                "distance_moved": distance,
                "position_after": actor.position,
            },
        )
        if fleeing:
            self._emit(
                encounter,
                "FLEE_ATTEMPTED",
                actor_id=action.actor_id,
                target_ids=(target_id,),
                payload={"action_id": action.action_id, "position_after": actor.position},
            )
            if abs(actor.position - target.position) >= B["disengage_distance"]:
                actor.escaped = True
                self._end_encounter(encounter, CombatStatus.DISENGAGED, "flee_success", action.actor_id)

    def _tick_bleeding(self, encounter: CombatEncounter) -> None:
        for actor_id, actor in encounter.actors.items():
            changed = actor.body.tick_bleeding()
            if changed:
                self._emit(
                    encounter,
                    "BLOOD_LOSS_CHANGED",
                    actor_id=actor_id,
                    target_ids=(actor_id,),
                    payload={"blood_loss_after": actor.body.blood_loss, "delta": changed},
                )
            if actor.body.dead:
                self._end_encounter(encounter, CombatStatus.DEATH_END, "bleeding", actor_id)
                return
            if actor.body.incapacitated:
                self._end_encounter(encounter, CombatStatus.INCAPACITATED_END, "bleeding", actor_id)
                return

    def _detect_attack(self, encounter: CombatEncounter, action: CombatAction, profile: CombatGuProfile) -> bool:
        target_state = encounter.actors[action.target_id or ""]
        if not target_state.perception_ready:
            return False
        perception_profile = self.profiles.get(target_state.perception_profile_id or "")
        if perception_profile is None:
            return False
        distance = abs(encounter.actors[action.actor_id].position - target_state.position)
        return distance <= B["disengage_distance"] and perception_profile.perception_strength >= profile.perceptibility

    def _latest_reaction_window(self, encounter: CombatEncounter, defender_id: str) -> ReactionWindow | None:
        candidates = [
            window
            for window in encounter.reaction_windows.values()
            if window.defender_id == defender_id and not window.resolved
        ]
        return max(candidates, key=lambda window: (window.opened_at_ms, window.attack_action_id), default=None)

    @staticmethod
    def _attack_for_window(encounter: CombatEncounter, window: ReactionWindow) -> CombatAction:
        for action in encounter.pending_actions:
            if action.action_id == window.attack_action_id:
                return action
        raise CombatValidationError("reaction window attack is no longer pending")

    def _end_encounter(
        self,
        encounter: CombatEncounter,
        status: CombatStatus,
        reason: str,
        actor_id: str,
    ) -> None:
        if encounter.status is not CombatStatus.ACTIVE:
            return
        encounter.status = status
        encounter.exit_reason = reason
        self._emit(
            encounter,
            "COMBAT_ENDED",
            actor_id=actor_id,
            target_ids=encounter.participants,
            payload={"status": status.value, "reason": reason},
        )

    def _reconcile_world_clock(self, encounter: CombatEncounter) -> None:
        target_seconds = encounter.world_clock_base_seconds + encounter.combat_time_ms // 1_000
        delta = target_seconds - self.world.clock.elapsed_seconds
        if delta > 0:
            self.world.clock.advance(delta)

    def _emit(
        self,
        encounter: CombatEncounter,
        event_type: str,
        *,
        actor_id: str | None,
        payload: dict[str, Any],
        target_ids: tuple[str, ...] = (),
    ) -> str:
        event = DomainEvent(
            event_id=self.world.entity_ids.next("event"),
            event_type=event_type,
            timestamp=self.world.clock.elapsed_seconds,
            actor_id=actor_id,
            target_ids=target_ids,
            location_id=encounter.location_id,
            payload={**payload, "encounter_id": encounter.encounter_id, "combat_time_ms": encounter.combat_time_ms},
            source="M2_COMBAT",
            provenance=Provenance.GAME_EXTENSION.value,
        )
        self.event_bus.publish(event)
        self.event_bus.dispatch_pending()
        return event.event_id

    def _active_encounter(self, encounter_id: str) -> CombatEncounter:
        try:
            encounter = self.encounters[encounter_id]
        except KeyError as exc:
            raise CombatValidationError(f"unknown encounter: {encounter_id}") from exc
        if encounter.status is not CombatStatus.ACTIVE:
            raise CombatValidationError("combat encounter is no longer active")
        return encounter

    def _profile_for_actor(self, profile_id: str, actor_id: str, role: CombatGuRole) -> CombatGuProfile:
        profile = self.profiles.get(profile_id)
        if profile is None or profile.role is not role:
            raise CombatValidationError("combat Gu profile role mismatch")
        character = self._character(actor_id)
        if profile.gu_instance_id not in character.owned_gu_ids:
            raise CombatValidationError("actor does not own the combat Gu")
        return profile

    def _validate_target(self, encounter: CombatEncounter, actor_id: str, target_id: str) -> None:
        if actor_id not in encounter.actors or target_id not in encounter.actors or actor_id == target_id:
            raise CombatValidationError("invalid combat target")

    def _require_essence(self, actor_id: str, cost: int) -> None:
        if self._character(actor_id).cultivation.primeval_current < cost:
            raise CombatValidationError("insufficient primeval essence")

    def _deduct_essence(self, actor_id: str, cost: int) -> None:
        self._character(actor_id).cultivation.primeval_current -= cost

    def _character(self, actor_id: str) -> Character:
        try:
            return self.simulation.characters[actor_id]
        except KeyError as exc:
            raise CombatValidationError(f"unknown character: {actor_id}") from exc
