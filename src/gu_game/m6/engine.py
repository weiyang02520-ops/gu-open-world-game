"""Deterministic M6 Rank-1 cultivation, breakthrough and attainment engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..m1.models import ResourceLot
from ..m1.simulation import ActionValidationError
from ..m3.engine import InformationEngine
from ..m4.engine import FactionEngine
from ..m5.engine import EconomyLogisticsEngine
from ..provenance import Provenance
from ..save import save_world
from .balance import GAME_EXTENSION_M6_BALANCE as B
from .models import (
    AttainmentRealm,
    BreakthroughMode,
    BreakthroughResult,
    CultivationMethod,
    CultivationProfile,
    InsightEvent,
    InsightType,
    KnowledgeRecord,
    MinorStage,
    PathAttainmentState,
    PathDefinition,
    StudySource,
)


class CultivationValidationError(ValueError):
    pass


class CultivationAttainmentEngine:
    """M6 layer sharing M1 characters, M5 economy and the authoritative WorldClock."""

    SCHEMA_VERSION = 1
    STAGE_SEQUENCE = (
        MinorStage.INITIAL,
        MinorStage.MIDDLE,
        MinorStage.UPPER,
        MinorStage.PEAK,
    )

    def __init__(self, economy: EconomyLogisticsEngine) -> None:
        self.economy = economy
        self.simulation = economy.simulation
        self.world = economy.world
        self.information = InformationEngine.from_simulation(self.simulation)
        self.factions = FactionEngine.from_simulation(self.simulation, self.information)
        self.methods: dict[str, CultivationMethod] = {}
        self.profiles: dict[str, CultivationProfile] = {}
        self.paths: dict[str, PathDefinition] = {}
        self.attainment: dict[str, PathAttainmentState] = {}
        self.insights: dict[str, InsightEvent] = {}
        self.knowledge: dict[str, KnowledgeRecord] = {}
        self.study_sources: dict[str, StudySource] = {}
        saved = self.world.game_state.get("m6_cultivation")
        if saved:
            self._load_dict(saved)
        else:
            self._bootstrap()
        self._sync_world_state()

    @classmethod
    def new(cls, seed: int) -> "CultivationAttainmentEngine":
        return cls(EconomyLogisticsEngine.new(seed))

    @classmethod
    def from_economy(cls, economy: EconomyLogisticsEngine) -> "CultivationAttainmentEngine":
        return cls(economy)

    @classmethod
    def load(cls, path: str | Path) -> "CultivationAttainmentEngine":
        return cls(EconomyLogisticsEngine.load(path))

    def save(self, path: str | Path) -> Path:
        self._sync_world_state()
        return save_world(self.world, path)

    def _bootstrap(self) -> None:
        self.methods["method-breath-cycle"] = CultivationMethod(
            "method-breath-cycle",
            "Steady Breath Cycle",
            progress_per_hour=8,
            essence_cost_per_hour=4,
            fatigue_per_hour=3,
        )
        self.methods["method-deep-circulation"] = CultivationMethod(
            "method-deep-circulation",
            "Deep Circulation",
            progress_per_hour=11,
            essence_cost_per_hour=6,
            fatigue_per_hour=5,
        )
        for path_id, name in (
            ("path-strength", "Strength Path"),
            ("path-wisdom", "Wisdom Path"),
            ("path-movement", "Movement Path"),
        ):
            self.paths[path_id] = PathDefinition(path_id, name)
        for character_id in self.simulation.characters:
            self.profiles[character_id] = CultivationProfile(character_id)
            for path_id in self.paths:
                state = PathAttainmentState(character_id, path_id)
                self.attainment[self._attainment_key(character_id, path_id)] = state
        self.study_sources["source-ash-inscription"] = StudySource(
            "source-ash-inscription",
            "Weathered Ash Inscription",
            "location-hidden-ash-grotto",
            "path-wisdom",
            "knowledge-ash-inscription-principle",
            base_insight=24,
            study_hours=3,
        )
        self.study_sources["source-river-footwork"] = StudySource(
            "source-river-footwork",
            "Riverbank Footwork Notes",
            "location-river-crossing",
            "path-movement",
            "knowledge-river-footwork",
            base_insight=18,
            study_hours=2,
        )

    def cultivate(
        self,
        character_id: str,
        *,
        hours: int = 1,
        method_id: str | None = None,
    ) -> dict[str, Any]:
        if hours <= 0 or hours > 12:
            raise CultivationValidationError("cultivation hours must be between 1 and 12")
        actor = self.simulation._character(character_id)
        cultivation = actor.cultivation
        if cultivation.rank != 1:
            raise CultivationValidationError("V0.1 M6 supports Rank 1 cultivation only")
        profile = self._profile(character_id)
        method = self.methods[method_id or profile.active_method_id]
        essence_cost = method.essence_cost_per_hour * hours
        if cultivation.primeval_current < essence_cost:
            raise CultivationValidationError("not enough primeval essence for cultivation session")

        wall_before = cultivation.wall_progress
        essence_before = cultivation.primeval_current
        fatigue_before = profile.fatigue
        quality_bonus = max(0, cultivation.essence_quality - 1) * hours
        fatigue_penalty = max(0, profile.fatigue - 70) * hours // 20
        progress = max(
            hours,
            method.progress_per_hour * hours + quality_bonus - fatigue_penalty,
        )
        cultivation.primeval_current -= essence_cost
        cultivation.wall_progress = min(
            cultivation.wall_threshold,
            cultivation.wall_progress + progress,
        )
        profile.fatigue = min(100, profile.fatigue + method.fatigue_per_hour * hours)
        profile.breakthrough_ready = cultivation.wall_progress >= cultivation.wall_threshold
        profile.last_session_at = self.world.clock.elapsed_seconds

        self.simulation._emit(
            "M6_CULTIVATION_SESSION",
            actor_id=character_id,
            location_id=actor.location_id,
            payload={
                "method_id": method.method_id,
                "hours": hours,
                "essence_before": essence_before,
                "essence_after": cultivation.primeval_current,
                "wall_progress_before": wall_before,
                "wall_progress_after": cultivation.wall_progress,
                "fatigue_before": fatigue_before,
                "fatigue_after": profile.fatigue,
                "breakthrough_ready": profile.breakthrough_ready,
                "provenance": Provenance.GAME_EXTENSION.value,
            },
        )
        self.advance_world(hours * 3_600)
        self._sync_world_state()
        return {
            "character_id": character_id,
            "hours": hours,
            "progress": cultivation.wall_progress - wall_before,
            "wall_progress": cultivation.wall_progress,
            "wall_threshold": cultivation.wall_threshold,
            "primeval_current": cultivation.primeval_current,
            "fatigue": profile.fatigue,
            "breakthrough_ready": profile.breakthrough_ready,
        }

    def cultivate_elapsed(
        self,
        character_id: str,
        *,
        hours: int = 1,
        method_id: str | None = None,
    ) -> dict[str, Any]:
        """Apply cultivation during time already advanced by a higher LOD layer.

        This uses the same Rank-1 cultivation economics as the normal cultivate
        action but deliberately does not advance WorldClock again. It is
        intended for remote or aggregated NPC simulation.
        """

        if hours <= 0 or hours > 12:
            raise CultivationValidationError(
                "elapsed cultivation hours must be between 1 and 12"
            )
        actor = self.simulation._character(character_id)
        cultivation = actor.cultivation
        if cultivation.rank != 1:
            raise CultivationValidationError(
                "V0.1 M6 supports Rank 1 cultivation only"
            )
        profile = self._profile(character_id)
        selected = self.methods[method_id or profile.active_method_id]
        essence_cost = selected.essence_cost_per_hour * hours
        if cultivation.primeval_current < essence_cost:
            return {
                "character_id": character_id,
                "hours": 0,
                "progress": 0,
                "reason": "insufficient_primeval_essence",
            }

        wall_before = cultivation.wall_progress
        essence_before = cultivation.primeval_current
        fatigue_before = profile.fatigue
        quality_bonus = max(0, cultivation.essence_quality - 1) * hours
        fatigue_penalty = max(0, profile.fatigue - 70) * hours // 20
        progress = max(
            hours,
            selected.progress_per_hour * hours
            + quality_bonus
            - fatigue_penalty,
        )
        cultivation.primeval_current -= essence_cost
        cultivation.wall_progress = min(
            cultivation.wall_threshold,
            cultivation.wall_progress + progress,
        )
        profile.fatigue = min(
            100, profile.fatigue + selected.fatigue_per_hour * hours
        )
        profile.breakthrough_ready = (
            cultivation.wall_progress >= cultivation.wall_threshold
        )
        profile.last_session_at = self.world.clock.elapsed_seconds

        self.simulation._emit(
            "M6_ABSTRACT_CULTIVATION_SESSION",
            actor_id=character_id,
            location_id=actor.location_id,
            payload={
                "method_id": selected.method_id,
                "hours": hours,
                "essence_before": essence_before,
                "essence_after": cultivation.primeval_current,
                "wall_progress_before": wall_before,
                "wall_progress_after": cultivation.wall_progress,
                "fatigue_before": fatigue_before,
                "fatigue_after": profile.fatigue,
                "breakthrough_ready": profile.breakthrough_ready,
                "time_already_advanced": True,
                "provenance": Provenance.GAME_EXTENSION.value,
            },
        )
        self._sync_world_state()
        return {
            "character_id": character_id,
            "hours": hours,
            "progress": cultivation.wall_progress - wall_before,
            "wall_progress": cultivation.wall_progress,
            "wall_threshold": cultivation.wall_threshold,
            "primeval_current": cultivation.primeval_current,
            "fatigue": profile.fatigue,
            "breakthrough_ready": profile.breakthrough_ready,
        }

    def rest(self, character_id: str, *, hours: int = 1) -> dict[str, int]:
        if hours <= 0 or hours > 24:
            raise CultivationValidationError("rest hours must be between 1 and 24")
        actor = self.simulation._character(character_id)
        profile = self._profile(character_id)
        before_essence = actor.cultivation.primeval_current
        before_fatigue = profile.fatigue
        before_instability = profile.instability
        self.advance_world(hours * 3_600)
        actor.cultivation.primeval_current = min(
            actor.cultivation.primeval_maximum,
            actor.cultivation.primeval_current + B["rest_essence_per_hour"] * hours,
        )
        profile.fatigue = max(0, profile.fatigue - B["rest_fatigue_per_hour"] * hours)
        profile.instability = max(
            0, profile.instability - B["rest_instability_per_hour"] * hours
        )
        self.simulation._emit(
            "M6_CULTIVATION_RESTED",
            actor_id=character_id,
            location_id=actor.location_id,
            payload={
                "hours": hours,
                "essence_before": before_essence,
                "essence_after": actor.cultivation.primeval_current,
                "fatigue_before": before_fatigue,
                "fatigue_after": profile.fatigue,
                "instability_before": before_instability,
                "instability_after": profile.instability,
            },
        )
        self._sync_world_state()
        return {
            "primeval_current": actor.cultivation.primeval_current,
            "fatigue": profile.fatigue,
            "instability": profile.instability,
        }

    def attempt_breakthrough(
        self,
        character_id: str,
        mode: BreakthroughMode = BreakthroughMode.SAFE,
    ) -> BreakthroughResult:
        actor = self.simulation._character(character_id)
        cultivation = actor.cultivation
        profile = self._profile(character_id)
        stage_before = MinorStage(cultivation.minor_stage)
        if stage_before is MinorStage.PEAK:
            raise CultivationValidationError("Rank 1 Peak is the V0.1 progression ceiling")

        progress_percent = (
            cultivation.wall_progress * 100 // max(1, cultivation.wall_threshold)
        )
        required = {
            BreakthroughMode.SAFE: B["safe_threshold_percent"],
            BreakthroughMode.SUPPORTED: B["supported_threshold_percent"],
            BreakthroughMode.FORCED: B["forced_threshold_percent"],
        }[mode]
        if progress_percent < required:
            raise CultivationValidationError(
                f"{mode.value} breakthrough requires {required}% wall progress"
            )

        support_resource_id: str | None = None
        if mode is BreakthroughMode.SUPPORTED:
            support_resource_id = B["supported_resource_id"]
            if actor.inventory_quantity(support_resource_id) < B["supported_resource_cost"]:
                raise CultivationValidationError("supported breakthrough requires support material")
            self.simulation._consume_from_collection(
                actor.inventory,
                support_resource_id,
                B["supported_resource_cost"],
            )

        roll: int | None = None
        target: int | None = None
        if mode is BreakthroughMode.SAFE:
            success = True
        elif mode is BreakthroughMode.SUPPORTED:
            target = max(
                30,
                B["supported_success_target"] - profile.fatigue // 5 - profile.instability // 4,
            )
            roll = self.world.rng.randint(1, 100)
            success = roll <= target
        else:
            profile.forced_attempts += 1
            progress_bonus = min(
                B["forced_progress_bonus_max"],
                max(0, progress_percent - B["forced_threshold_percent"]),
            )
            target = max(
                10,
                min(
                    90,
                    B["forced_base_success"]
                    + progress_bonus
                    + max(0, cultivation.essence_quality - 1) * 5
                    - profile.fatigue // 4
                    - profile.instability // 3,
                ),
            )
            roll = self.world.rng.randint(1, 100)
            success = roll <= target

        next_stage = self.STAGE_SEQUENCE[self.STAGE_SEQUENCE.index(stage_before) + 1]
        if success:
            cultivation.minor_stage = next_stage.value
            cultivation.wall_progress = 0
            cultivation.wall_threshold += 20
            aptitude_capacity_gain = B["success_capacity_gain"] + cultivation.aptitude // 20
            cultivation.aperture_capacity += aptitude_capacity_gain
            cultivation.primeval_maximum += B["success_essence_max_gain"]
            cultivation.primeval_current = min(
                cultivation.primeval_maximum,
                cultivation.primeval_current + B["success_essence_max_gain"] // 2,
            )
            cultivation.essence_quality = min(4, cultivation.essence_quality + 1)
            profile.breakthrough_ready = False
            profile.instability = max(0, profile.instability - 10)
            if mode is BreakthroughMode.SAFE:
                profile.safe_breakthroughs += 1
            consequence = "stage_advanced"
            stage_after = next_stage
        else:
            cultivation.wall_progress = max(
                0, cultivation.wall_progress - B["failure_wall_regression"]
            )
            profile.instability = min(
                100, profile.instability + B["failure_instability_gain"]
            )
            profile.health_modifier = max(
                10, profile.health_modifier - B["failure_health_loss"]
            )
            profile.breakthrough_ready = (
                cultivation.wall_progress >= cultivation.wall_threshold
            )
            consequence = "instability_and_regression"
            stage_after = stage_before

        fatigue_cost = {
            BreakthroughMode.SAFE: B["safe_fatigue_cost"],
            BreakthroughMode.SUPPORTED: B["supported_fatigue_cost"],
            BreakthroughMode.FORCED: B["forced_fatigue_cost"],
        }[mode]
        profile.fatigue = min(100, profile.fatigue + fatigue_cost)
        self.simulation._emit(
            "M6_BREAKTHROUGH_RESOLVED",
            actor_id=character_id,
            location_id=actor.location_id,
            payload={
                "mode": mode.value,
                "success": success,
                "stage_before": stage_before.value,
                "stage_after": stage_after.value,
                "progress_percent": progress_percent,
                "roll": roll,
                "target": target,
                "support_resource_id": support_resource_id,
                "fatigue_after": profile.fatigue,
                "instability_after": profile.instability,
                "health_modifier_after": profile.health_modifier,
                "provenance": Provenance.GAME_EXTENSION.value,
            },
        )
        self.advance_world(B["breakthrough_duration_seconds"])
        result = BreakthroughResult(
            character_id,
            mode,
            success,
            stage_before,
            stage_after,
            roll,
            target,
            consequence,
        )
        self._sync_world_state()
        return result

    def gain_insight(
        self,
        character_id: str,
        path_id: str,
        *,
        insight_type: InsightType,
        source_key: str,
        base_value: int,
    ) -> InsightEvent:
        if base_value <= 0:
            raise CultivationValidationError("base insight must be positive")
        if path_id not in self.paths:
            raise CultivationValidationError("unknown path")
        state = self._attainment(character_id, path_id)
        repeats = state.novelty_history.get(source_key, 0)
        novelty = 100
        for _ in range(repeats):
            novelty = max(
                B["insight_min_percent"],
                novelty * B["insight_repeat_decay_percent"] // 100,
            )
        awarded = max(1, base_value * novelty // 100)
        state.novelty_history[source_key] = repeats + 1
        state.insight_points += awarded
        realm_before = state.realm
        state.refresh_realm()
        insight = InsightEvent(
            self.world.entity_ids.next("insight"),
            character_id,
            path_id,
            insight_type,
            source_key,
            base_value,
            awarded,
            novelty,
            self.world.clock.elapsed_seconds,
        )
        self.insights[insight.insight_id] = insight
        self.simulation._emit(
            "M6_INSIGHT_GAINED",
            actor_id=character_id,
            target_ids=(path_id,),
            location_id=self.simulation._character(character_id).location_id,
            payload={
                "insight_id": insight.insight_id,
                "insight_type": insight_type.value,
                "source_key": source_key,
                "base_value": base_value,
                "awarded_value": awarded,
                "novelty_factor": novelty,
                "points_after": state.insight_points,
                "realm_before": realm_before.value,
                "realm_after": state.realm.value,
            },
        )
        self._sync_world_state()
        return insight

    def study(self, character_id: str, source_id: str) -> dict[str, Any]:
        source = self.study_sources.get(source_id)
        if source is None:
            raise CultivationValidationError("unknown study source")
        actor = self.simulation._character(character_id)
        existing = next(
            (
                item
                for item in self.knowledge.values()
                if item.character_id == character_id
                and item.subject_id == source.knowledge_subject_id
            ),
            None,
        )
        if existing is None:
            record = KnowledgeRecord(
                self.world.entity_ids.next("knowledge"),
                character_id,
                "TECHNIQUE",
                source.knowledge_subject_id,
                self.world.clock.elapsed_seconds,
                source.source_id,
            )
            self.knowledge[record.knowledge_id] = record
        else:
            existing.proficiency = min(100, existing.proficiency + 1)
            record = existing
        insight = self.gain_insight(
            character_id,
            source.path_id,
            insight_type=InsightType.INHERITANCE
            if "hidden" in source.location_id
            else InsightType.STUDY,
            source_key=source.source_id,
            base_value=source.base_insight,
        )
        self.advance_world(source.study_hours * 3_600)
        self.simulation._emit(
            "M6_STUDY_COMPLETED",
            actor_id=character_id,
            location_id=actor.location_id,
            payload={
                "source_id": source.source_id,
                "knowledge_id": record.knowledge_id,
                "subject_id": record.subject_id,
                "path_id": source.path_id,
                "insight_id": insight.insight_id,
                "hours": source.study_hours,
            },
        )
        self._sync_world_state()
        return {
            "knowledge_id": record.knowledge_id,
            "subject_id": record.subject_id,
            "attainment_realm": self._attainment(character_id, source.path_id).realm.value,
            "insight_awarded": insight.awarded_value,
        }

    def advance_world(self, seconds: int) -> None:
        """Advance the authoritative clock once, then process all integrated layers."""
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        self.economy.advance_time(seconds, run_npcs=True)
        self.information.process_elapsed_time(seconds)
        self.factions.process_elapsed_time(seconds)
        self._sync_world_state()

    def summary(self, character_id: str | None = None) -> dict[str, Any]:
        character_id = character_id or self.simulation.player_id
        actor = self.simulation._character(character_id)
        profile = self._profile(character_id)
        return {
            "phase": "M6",
            "character_id": character_id,
            "rank": actor.cultivation.rank,
            "stage": actor.cultivation.minor_stage,
            "aptitude": actor.cultivation.aptitude,
            "aperture_capacity": actor.cultivation.aperture_capacity,
            "primeval_current": actor.cultivation.primeval_current,
            "primeval_maximum": actor.cultivation.primeval_maximum,
            "essence_quality": actor.cultivation.essence_quality,
            "wall_progress": actor.cultivation.wall_progress,
            "wall_threshold": actor.cultivation.wall_threshold,
            "fatigue": profile.fatigue,
            "instability": profile.instability,
            "health_modifier": profile.health_modifier,
            "breakthrough_ready": profile.breakthrough_ready,
            "attainment": {
                path_id: self._attainment(character_id, path_id).to_dict()
                for path_id in sorted(self.paths)
            },
            "knowledge": [
                item.to_dict()
                for item in self.knowledge.values()
                if item.character_id == character_id
            ],
            "world_day": self.world.clock.day_number,
            "economy": self.economy.summary(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "methods": {key: value.to_dict() for key, value in sorted(self.methods.items())},
            "profiles": {key: value.to_dict() for key, value in sorted(self.profiles.items())},
            "paths": {key: value.to_dict() for key, value in sorted(self.paths.items())},
            "attainment": {key: value.to_dict() for key, value in sorted(self.attainment.items())},
            "insights": {key: value.to_dict() for key, value in sorted(self.insights.items())},
            "knowledge": {key: value.to_dict() for key, value in sorted(self.knowledge.items())},
            "study_sources": {
                key: value.to_dict() for key, value in sorted(self.study_sources.items())
            },
        }

    def _load_dict(self, data: dict[str, Any]) -> None:
        if int(data.get("schema_version", 0)) > self.SCHEMA_VERSION:
            raise ValueError("M6 save is newer than this engine")
        self.methods = {
            key: CultivationMethod.from_dict(value)
            for key, value in data.get("methods", {}).items()
        }
        self.profiles = {
            key: CultivationProfile.from_dict(value)
            for key, value in data.get("profiles", {}).items()
        }
        self.paths = {
            key: PathDefinition.from_dict(value)
            for key, value in data.get("paths", {}).items()
        }
        self.attainment = {
            key: PathAttainmentState.from_dict(value)
            for key, value in data.get("attainment", {}).items()
        }
        self.insights = {
            key: InsightEvent.from_dict(value)
            for key, value in data.get("insights", {}).items()
        }
        self.knowledge = {
            key: KnowledgeRecord.from_dict(value)
            for key, value in data.get("knowledge", {}).items()
        }
        self.study_sources = {
            key: StudySource.from_dict(value)
            for key, value in data.get("study_sources", {}).items()
        }

    def _sync_world_state(self) -> None:
        # Each layer writes back through the shared Simulation, preserving sibling domains.
        self.information._sync_world_state()
        self.factions._sync_world_state()
        self.economy._sync_world_state()
        self.world.game_state["m6_cultivation"] = self.to_dict()

    def _profile(self, character_id: str) -> CultivationProfile:
        if character_id not in self.profiles:
            self.profiles[character_id] = CultivationProfile(character_id)
        return self.profiles[character_id]

    def _attainment(self, character_id: str, path_id: str) -> PathAttainmentState:
        key = self._attainment_key(character_id, path_id)
        if key not in self.attainment:
            self.attainment[key] = PathAttainmentState(character_id, path_id)
        return self.attainment[key]

    @staticmethod
    def _attainment_key(character_id: str, path_id: str) -> str:
        return f"{character_id}:{path_id}"
