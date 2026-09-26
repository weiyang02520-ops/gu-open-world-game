"""Deterministic M7 effect graphs and killer-move research."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..m2.engine import CombatEngine, CombatValidationError
from ..m2.models import BodyPart, CombatGuRole, CombatStatus
from ..m6.engine import CultivationAttainmentEngine
from ..m6.models import AttainmentRealm, InsightType
from ..provenance import Provenance
from ..save import save_world
from .balance import GAME_EXTENSION_M7_BALANCE as B
from .models import (
    EffectExecutionResult,
    EffectGraph,
    EffectNode,
    EffectNodeType,
    KillerMoveDefinition,
    KillerMoveInstance,
    KillerMoveMastery,
)


class EffectGraphValidationError(ValueError):
    pass


class EffectGraphEngine:
    """M7 compositional layer over M2 combat and M6 attainment."""

    SCHEMA_VERSION = 1

    def __init__(self, cultivation: CultivationAttainmentEngine) -> None:
        self.cultivation = cultivation
        self.simulation = cultivation.simulation
        self.world = cultivation.world
        self.combat = CombatEngine.from_simulation(self.simulation)
        self.graphs: dict[str, EffectGraph] = {}
        self.profile_graphs: dict[str, str] = {}
        self.definitions: dict[str, KillerMoveDefinition] = {}
        self.instances: dict[str, KillerMoveInstance] = {}
        self.research_history: list[dict[str, Any]] = []
        saved = self.world.game_state.get("m7_killer_moves")
        if saved:
            self._load_dict(saved)
        else:
            self._bootstrap_profile_graphs()
        self._sync_world_state()

    @classmethod
    def new(cls, seed: int) -> "EffectGraphEngine":
        return cls(CultivationAttainmentEngine.new(seed))

    @classmethod
    def from_cultivation(cls, cultivation: CultivationAttainmentEngine) -> "EffectGraphEngine":
        return cls(cultivation)

    @classmethod
    def load(cls, path: str | Path) -> "EffectGraphEngine":
        return cls(CultivationAttainmentEngine.load(path))

    def save(self, path: str | Path) -> Path:
        self._sync_world_state()
        return save_world(self.world, path)

    def _bootstrap_profile_graphs(self) -> None:
        """Create declarative mirrors for every M2 combat Gu profile."""
        for profile_id, profile in sorted(self.combat.profiles.items()):
            graph_id = f"effect-graph::{profile_id}"
            if profile.role is CombatGuRole.ATTACK:
                nodes = self._chain(
                    graph_id,
                    [
                        (EffectNodeType.DELAY, {"milliseconds": profile.preparation_ticks * 250}),
                        (EffectNodeType.CHECK_RANGE, {"range": profile.range}),
                        (EffectNodeType.APPLY_INJURY, {"power": profile.effect_power, "body_part": profile.target_part.value}),
                        (EffectNodeType.END, {}),
                    ],
                )
            elif profile.role is CombatGuRole.MOVEMENT:
                nodes = self._chain(
                    graph_id,
                    [
                        (EffectNodeType.DELAY, {"milliseconds": profile.preparation_ticks * 250}),
                        (EffectNodeType.MOVE, {"distance": profile.movement_distance, "direction": "away"}),
                        (EffectNodeType.END, {}),
                    ],
                )
            else:
                nodes = self._chain(
                    graph_id,
                    [
                        (EffectNodeType.DELAY, {"milliseconds": profile.preparation_ticks * 250}),
                        (EffectNodeType.DETECT, {"strength": profile.perception_strength}),
                        (EffectNodeType.END, {}),
                    ],
                )
            graph = EffectGraph(graph_id, next(iter(nodes)), nodes)
            self.graphs[graph_id] = graph
            self.profile_graphs[profile_id] = graph_id

    def design_killer_move(
        self,
        owner_id: str,
        name: str,
        gu_instance_ids: list[str],
        path_id: str,
    ) -> KillerMoveInstance:
        if len(set(gu_instance_ids)) != len(gu_instance_ids) or len(gu_instance_ids) < 2:
            raise EffectGraphValidationError("killer move requires at least two unique Gu")
        if path_id not in self.cultivation.paths:
            raise EffectGraphValidationError("unknown path")
        actor = self.simulation._character(owner_id)
        profiles = []
        for gu_id in gu_instance_ids:
            gu = self.simulation.gu_instances.get(gu_id)
            if gu is None or gu.owner_id != owner_id:
                raise EffectGraphValidationError("actor must own every component Gu")
            if gu.condition < B["minimum_gu_condition"]:
                raise EffectGraphValidationError("component Gu condition is too low")
            definition = self.simulation.gu_definitions[gu.definition_id]
            if definition.rank > actor.cultivation.rank:
                raise EffectGraphValidationError("component Gu rank exceeds actor rank")
            matching = [p for p in self.combat.profiles.values() if p.gu_instance_id == gu_id]
            if not matching:
                raise EffectGraphValidationError("component Gu lacks an executable effect profile")
            profiles.extend(matching)

        selected = self._select_component_profiles(gu_instance_ids, profiles)
        if not any(profile.role is CombatGuRole.ATTACK for profile in selected):
            raise EffectGraphValidationError("V0.1 killer move requires an attack component")

        complexity = len(gu_instance_ids)
        attainment = self.cultivation._attainment(owner_id, path_id)
        max_complexity = self._max_complexity(attainment.realm)
        if complexity > max_complexity:
            raise EffectGraphValidationError(
                f"{attainment.realm.value} attainment cannot control complexity {complexity}"
            )

        conditions = [self.simulation.gu_instances[gu_id].condition for gu_id in gu_instance_ids]
        stability = B["base_stability"] + sum(conditions) // len(conditions) // B["condition_bonus_divisor"]
        stability += self._attainment_stability_bonus(attainment.realm)
        stability -= complexity * B["complexity_penalty"]
        stability = max(20, min(99, stability))

        role_order = {CombatGuRole.PERCEPTION: 0, CombatGuRole.MOVEMENT: 1, CombatGuRole.ATTACK: 2}
        selected.sort(key=lambda item: (role_order[item.role], item.profile_id))
        attack = next(item for item in selected if item.role is CombatGuRole.ATTACK)
        perception = next((item for item in selected if item.role is CombatGuRole.PERCEPTION), None)
        movement = next((item for item in selected if item.role is CombatGuRole.MOVEMENT), None)
        total_prep_ms = sum(item.preparation_ticks * 250 for item in selected)
        combined_prep_ms = max(250, total_prep_ms * B["combined_preparation_percent"] // 100)
        graph_id = self.world.entity_ids.next("effect-graph")
        steps: list[tuple[EffectNodeType, dict[str, Any]]] = []
        if perception:
            steps.append((EffectNodeType.DETECT, {"strength": perception.perception_strength}))
        steps.append((EffectNodeType.DELAY, {"milliseconds": combined_prep_ms}))
        if movement:
            steps.append((EffectNodeType.MOVE, {"distance": movement.movement_distance, "direction": "toward"}))
        steps.append((EffectNodeType.CHECK_RANGE, {"range": attack.range}))
        steps.append((EffectNodeType.APPLY_INJURY, {"power": attack.effect_power, "body_part": attack.target_part.value}))
        steps.append((EffectNodeType.END, {}))
        nodes = self._chain(graph_id, steps)
        self.graphs[graph_id] = EffectGraph(graph_id, next(iter(nodes)), nodes)

        minimum = self._minimum_realm_for_complexity(complexity)
        killer_move_id = self.world.entity_ids.next("killer-move")
        definition = KillerMoveDefinition(
            killer_move_id=killer_move_id,
            name=name,
            creator_id=owner_id,
            core_gu_ids=[attack.gu_instance_id],
            auxiliary_gu_ids=[gu_id for gu_id in gu_instance_ids if gu_id != attack.gu_instance_id],
            path_id=path_id,
            activation_order=[profile.gu_instance_id for profile in selected],
            graph_id=graph_id,
            essence_cost=sum(profile.essence_cost for profile in selected),
            preparation_ms=combined_prep_ms,
            stability=stability,
            complexity=complexity,
            minimum_attainment=minimum,
        )
        self.definitions[killer_move_id] = definition
        instance_id = self.world.entity_ids.next("killer-move-instance")
        instance = KillerMoveInstance(
            instance_id, killer_move_id, owner_id, self._mastery_for(stability)
        )
        self.instances[instance_id] = instance
        self.simulation._emit(
            "M7_KILLER_MOVE_DISCOVERED",
            actor_id=owner_id,
            target_ids=tuple(gu_instance_ids),
            location_id=actor.location_id,
            payload={
                "killer_move_id": killer_move_id,
                "instance_id": instance_id,
                "path_id": path_id,
                "complexity": complexity,
                "stability": stability,
                "mastery": instance.mastery.value,
                "graph_id": graph_id,
                "provenance": Provenance.GAME_EXTENSION.value,
            },
        )
        self._sync_world_state()
        return instance

    def research_killer_move(self, instance_id: str) -> KillerMoveInstance:
        instance = self.instances[instance_id]
        definition = self.definitions[instance.definition_id]
        actor = self.simulation._character(instance.owner_id)
        material_id = B["research_material_id"]
        quantity = B["research_material_quantity"]
        if actor.inventory_quantity(material_id) < quantity:
            raise EffectGraphValidationError("killer-move research requires refinement material")
        self.simulation._consume_from_collection(actor.inventory, material_id, quantity)
        attainment = self.cultivation._attainment(instance.owner_id, definition.path_id)
        insight = self.cultivation.gain_insight(
            instance.owner_id,
            definition.path_id,
            insight_type=InsightType.EXPERIMENTATION,
            source_key=f"killer-move-research:{definition.killer_move_id}",
            base_value=12,
        )
        gain = B["research_stability_gain"] + self._attainment_stability_bonus(attainment.realm) // 2
        gain += insight.awarded_value // 10
        instance.stability_modifier = min(30, instance.stability_modifier + gain)
        instance.research_count += 1
        instance.mastery = self._mastery_for(self.effective_stability(instance_id))
        self.cultivation.advance_world(B["research_hours"] * 3_600)
        self.research_history.append({
            "instance_id": instance_id,
            "time": self.world.clock.elapsed_seconds,
            "material_id": material_id,
            "stability_gain": gain,
            "mastery": instance.mastery.value,
        })
        self.simulation._emit(
            "M7_KILLER_MOVE_RESEARCHED",
            actor_id=instance.owner_id,
            location_id=actor.location_id,
            payload={
                "instance_id": instance_id,
                "research_count": instance.research_count,
                "effective_stability": self.effective_stability(instance_id),
                "mastery": instance.mastery.value,
                "material_id": material_id,
                "insight_id": insight.insight_id,
            },
        )
        self._sync_world_state()
        return instance

    def execute_killer_move(
        self,
        instance_id: str,
        encounter_id: str,
        actor_id: str,
        target_id: str,
    ) -> EffectExecutionResult:
        instance = self.instances[instance_id]
        definition = self.definitions[instance.definition_id]
        if instance.owner_id != actor_id:
            raise EffectGraphValidationError("actor does not own this killer move")
        encounter = self.combat._active_encounter(encounter_id)
        if actor_id not in encounter.actors or target_id not in encounter.actors or actor_id == target_id:
            raise EffectGraphValidationError("invalid killer-move target")
        actor = self.simulation._character(actor_id)
        all_gu = definition.core_gu_ids + definition.auxiliary_gu_ids
        for gu_id in all_gu:
            gu = self.simulation.gu_instances.get(gu_id)
            if gu is None or gu.owner_id != actor_id:
                raise EffectGraphValidationError("killer-move component ownership changed")
            if gu.condition < B["minimum_gu_condition"]:
                raise EffectGraphValidationError("killer-move component condition too low")
        if actor.cultivation.primeval_current < definition.essence_cost:
            raise EffectGraphValidationError("insufficient primeval essence")
        attainment = self.cultivation._attainment(actor_id, definition.path_id)
        if self._realm_rank(attainment.realm) < self._realm_rank(definition.minimum_attainment):
            raise EffectGraphValidationError("current attainment no longer meets killer-move requirement")

        effective = self.effective_stability(instance_id)
        roll = self.world.rng.randint(1, 100)
        instance.last_test_at = self.world.clock.elapsed_seconds
        unstable_failure = effective < 10 or (
            effective < B["proficient_threshold"] and roll > effective
        )
        if unstable_failure:
            essence_spent = max(1, definition.essence_cost // 2)
            actor.cultivation.primeval_current -= essence_spent
            injury = encounter.actors[actor_id].body.apply_hit(
                BodyPart.RIGHT_ARM, B["backlash_self_power"]
            )
            for gu_id in all_gu:
                self.simulation.gu_instances[gu_id].condition = max(
                    0,
                    self.simulation.gu_instances[gu_id].condition - B["backlash_gu_condition_loss"],
                )
            self.combat._emit(
                encounter,
                "M7_KILLER_MOVE_BACKLASH",
                actor_id=actor_id,
                target_ids=(actor_id,),
                payload={
                    "instance_id": instance_id,
                    "roll": roll,
                    "effective_stability": effective,
                    "essence_spent": essence_spent,
                    "body_part": injury.part.value,
                    "impairment": injury.impairment,
                },
            )
            self._sync_world_state()
            return EffectExecutionResult(
                False, instance_id, tuple(), essence_spent, "backlash", True
            )

        actor.cultivation.primeval_current -= definition.essence_cost
        graph = self.graphs[definition.graph_id]
        executed, outcome = self._execute_graph(graph, encounter_id, actor_id, target_id)
        success = outcome == "completed"
        instance.mastery = self._mastery_for(effective)
        self.combat._emit(
            encounter,
            "M7_KILLER_MOVE_EXECUTED",
            actor_id=actor_id,
            target_ids=(target_id,),
            payload={
                "instance_id": instance_id,
                "killer_move_id": definition.killer_move_id,
                "graph_id": definition.graph_id,
                "effective_stability": effective,
                "roll": roll,
                "success": success,
                "outcome": outcome,
                "essence_cost": definition.essence_cost,
                "executed_nodes": list(executed),
            },
        )
        self._sync_world_state()
        return EffectExecutionResult(
            success, instance_id, tuple(executed), definition.essence_cost, outcome, False
        )

    def _execute_graph(
        self, graph: EffectGraph, encounter_id: str, actor_id: str, target_id: str
    ) -> tuple[list[str], str]:
        encounter = self.combat._active_encounter(encounter_id)
        current = graph.entry_node_id
        executed: list[str] = []
        guard = 0
        while current:
            guard += 1
            if guard > len(graph.nodes) + 2:
                raise EffectGraphValidationError("effect graph cycle detected")
            node = graph.nodes[current]
            executed.append(node.node_id)
            self.combat._emit(
                encounter,
                "M7_EFFECT_NODE_EXECUTED",
                actor_id=actor_id,
                target_ids=(target_id,),
                payload={"graph_id": graph.graph_id, "node_id": node.node_id, "node_type": node.node_type.value},
            )
            if node.node_type is EffectNodeType.DELAY:
                milliseconds = max(0, int(node.parameters.get("milliseconds", 0)))
                ticks = (milliseconds + encounter.tick_ms - 1) // encounter.tick_ms
                if ticks:
                    self.combat.advance_ticks(encounter_id, ticks)
                    if encounter.status is not CombatStatus.ACTIVE:
                        return executed, "encounter_ended_during_preparation"
            elif node.node_type is EffectNodeType.DETECT:
                encounter.actors[actor_id].perception_ready = True
            elif node.node_type is EffectNodeType.MOVE:
                actor_state = encounter.actors[actor_id]
                target_state = encounter.actors[target_id]
                raw_distance = int(node.parameters.get("distance", 0))
                distance = actor_state.body.movement_distance(raw_distance)
                current_distance = abs(actor_state.position - target_state.position)
                direction = str(node.parameters.get("direction", "away"))
                sign = 1 if actor_state.position >= target_state.position else -1
                if direction == "toward":
                    step = min(distance, max(0, current_distance - 1))
                    actor_state.position -= sign * step
                else:
                    actor_state.position += sign * distance
            elif node.node_type is EffectNodeType.CHECK_RANGE:
                actor_state = encounter.actors[actor_id]
                target_state = encounter.actors[target_id]
                allowed = int(node.parameters.get("range", 0))
                if abs(actor_state.position - target_state.position) > allowed:
                    return executed, "range_check_failed"
            elif node.node_type is EffectNodeType.APPLY_INJURY:
                target_state = encounter.actors[target_id]
                part = BodyPart(str(node.parameters.get("body_part", BodyPart.LEFT_LEG.value)))
                power = int(node.parameters.get("power", 0))
                injury = target_state.body.apply_hit(part, power)
                self.combat._emit(
                    encounter,
                    "INJURY_APPLIED",
                    actor_id=actor_id,
                    target_ids=(target_id,),
                    payload={
                        "source": "M7_EFFECT_GRAPH",
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
                    self.combat._end_encounter(encounter, CombatStatus.DEATH_END, "m7_effect_graph_fatal", target_id)
                    return executed, "target_killed"
                if injury.incapacitating:
                    self.combat._end_encounter(encounter, CombatStatus.INCAPACITATED_END, "m7_effect_graph_incapacitated", target_id)
                    return executed, "target_incapacitated"
            elif node.node_type is EffectNodeType.END:
                return executed, "completed"
            current = node.next_node_id
        return executed, "completed"

    def effective_stability(self, instance_id: str) -> int:
        instance = self.instances[instance_id]
        definition = self.definitions[instance.definition_id]
        return max(1, min(99, definition.stability + instance.stability_modifier))

    def summary(self, owner_id: str | None = None) -> dict[str, Any]:
        owner_id = owner_id or self.simulation.player_id
        return {
            "phase": "M7",
            "graphs": len(self.graphs),
            "legacy_profile_graphs": len(self.profile_graphs),
            "killer_moves": [
                {
                    "instance_id": instance.instance_id,
                    "definition_id": instance.definition_id,
                    "name": self.definitions[instance.definition_id].name,
                    "path_id": self.definitions[instance.definition_id].path_id,
                    "complexity": self.definitions[instance.definition_id].complexity,
                    "effective_stability": self.effective_stability(instance.instance_id),
                    "mastery": instance.mastery.value,
                    "research_count": instance.research_count,
                }
                for instance in self.instances.values()
                if instance.owner_id == owner_id
            ],
            "research_history": list(self.research_history),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "graphs": {key: value.to_dict() for key, value in sorted(self.graphs.items())},
            "profile_graphs": dict(self.profile_graphs),
            "definitions": {key: value.to_dict() for key, value in sorted(self.definitions.items())},
            "instances": {key: value.to_dict() for key, value in sorted(self.instances.items())},
            "research_history": list(self.research_history),
        }

    def _load_dict(self, data: dict[str, Any]) -> None:
        if int(data.get("schema_version", 0)) > self.SCHEMA_VERSION:
            raise ValueError("M7 save is newer than this engine")
        self.graphs = {key: EffectGraph.from_dict(value) for key, value in data.get("graphs", {}).items()}
        self.profile_graphs = {str(k): str(v) for k, v in data.get("profile_graphs", {}).items()}
        self.definitions = {
            key: KillerMoveDefinition.from_dict(value)
            for key, value in data.get("definitions", {}).items()
        }
        self.instances = {
            key: KillerMoveInstance.from_dict(value)
            for key, value in data.get("instances", {}).items()
        }
        self.research_history = list(data.get("research_history", []))
        if not self.profile_graphs:
            self._bootstrap_profile_graphs()

    def _sync_world_state(self) -> None:
        self.cultivation._sync_world_state()
        self.combat._sync_world_state()
        self.world.game_state["m7_killer_moves"] = self.to_dict()

    @staticmethod
    def _chain(
        graph_id: str, steps: list[tuple[EffectNodeType, dict[str, Any]]]
    ) -> dict[str, EffectNode]:
        nodes: dict[str, EffectNode] = {}
        ids = [f"{graph_id}:node:{index:02d}" for index in range(len(steps))]
        for index, (node_type, params) in enumerate(steps):
            nodes[ids[index]] = EffectNode(
                ids[index],
                node_type,
                dict(params),
                ids[index + 1] if index + 1 < len(ids) else None,
            )
        return nodes

    def _select_component_profiles(self, gu_ids: list[str], profiles: list[Any]) -> list[Any]:
        role_priority = [CombatGuRole.PERCEPTION, CombatGuRole.MOVEMENT, CombatGuRole.ATTACK]
        selected = []
        used_gu: set[str] = set()
        for role in role_priority:
            match = next(
                (p for p in profiles if p.role is role and p.gu_instance_id in gu_ids and p.gu_instance_id not in used_gu),
                None,
            )
            if match:
                selected.append(match)
                used_gu.add(match.gu_instance_id)
        for gu_id in gu_ids:
            if gu_id in used_gu:
                continue
            match = next((p for p in profiles if p.gu_instance_id == gu_id), None)
            if match:
                selected.append(match)
                used_gu.add(gu_id)
        return selected

    @staticmethod
    def _realm_rank(realm: AttainmentRealm) -> int:
        return {
            AttainmentRealm.ORDINARY: 0,
            AttainmentRealm.QUASI_MASTER: 1,
            AttainmentRealm.MASTER: 2,
        }[realm]

    def _max_complexity(self, realm: AttainmentRealm) -> int:
        return {
            AttainmentRealm.ORDINARY: B["ordinary_max_complexity"],
            AttainmentRealm.QUASI_MASTER: B["quasi_master_max_complexity"],
            AttainmentRealm.MASTER: B["master_max_complexity"],
        }[realm]

    @staticmethod
    def _minimum_realm_for_complexity(complexity: int) -> AttainmentRealm:
        if complexity <= 2:
            return AttainmentRealm.ORDINARY
        if complexity <= 3:
            return AttainmentRealm.QUASI_MASTER
        return AttainmentRealm.MASTER

    @staticmethod
    def _attainment_stability_bonus(realm: AttainmentRealm) -> int:
        return {
            AttainmentRealm.ORDINARY: 0,
            AttainmentRealm.QUASI_MASTER: B["quasi_master_stability_bonus"],
            AttainmentRealm.MASTER: B["master_stability_bonus"],
        }[realm]

    @staticmethod
    def _mastery_for(stability: int) -> KillerMoveMastery:
        if stability < B["unstable_threshold"]:
            return KillerMoveMastery.UNSTABLE
        if stability < B["discovered_threshold"]:
            return KillerMoveMastery.DISCOVERED
        if stability < B["usable_threshold"]:
            return KillerMoveMastery.USABLE
        if stability < B["proficient_threshold"]:
            return KillerMoveMastery.PROFICIENT
        return KillerMoveMastery.MASTERED
