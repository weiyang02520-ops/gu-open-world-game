from __future__ import annotations

from pathlib import Path

from gu_game.m8.engine import IntegratedV01Engine
from gu_game.m8.models import CanonAnchorStatus, SimulationLevel, StrategyProfile
from gu_game.m8.scenario import run_v01_comparison, run_v01_smoke


def test_m8_content_targets_and_world_lod() -> None:
    engine = IntegratedV01Engine.new(801)
    snapshot = engine.snapshot()
    content = snapshot["content"]

    assert 20 <= content["locations"] <= 40
    assert content["important_npcs"] >= 15
    assert 3 <= content["factions"] <= 5
    assert 30 <= content["gu_definitions"] <= 50
    assert content["feeding_requirements"] >= 20
    assert 15 <= content["resource_nodes"] <= 25
    assert 3 <= content["markets"] <= 4
    assert 5 <= content["routes"] <= 8

    levels = {location.level for location in engine.locations.values()}
    assert SimulationLevel.ACTIVE in levels
    assert SimulationLevel.NEAR in levels
    assert SimulationLevel.REGIONAL in levels
    assert SimulationLevel.ABSTRACT in levels
    assert any(location.hidden for location in engine.locations.values())


def test_m8_canon_anchor_scaffold_is_conditional_not_forced() -> None:
    engine = IntegratedV01Engine.new(802)
    assert engine.anchors
    assert all(anchor.provenance == "GAME_EXTENSION" for anchor in engine.anchors.values())
    assert all(anchor.prerequisites for anchor in engine.anchors.values())
    assert all(anchor.status is CanonAnchorStatus.PENDING for anchor in engine.anchors.values())

    engine.evaluate_anchors()
    assert all(anchor.status is CanonAnchorStatus.PENDING for anchor in engine.anchors.values())


def test_m8_cooperative_day10_smoke() -> None:
    result = run_v01_smoke(803, StrategyProfile.COOPERATIVE)
    snapshot = result["snapshot"]

    assert snapshot["completed_day"] == 10
    assert snapshot["days_elapsed"] >= 10
    assert snapshot["strategy"] == StrategyProfile.COOPERATIVE.value
    assert len(result["day_history"]) == 10
    assert snapshot["event_count"] > 0
    assert snapshot["killer_moves"]


def test_m8_adversarial_day10_smoke() -> None:
    result = run_v01_smoke(804, StrategyProfile.ADVERSARIAL)
    snapshot = result["snapshot"]

    assert snapshot["completed_day"] == 10
    assert snapshot["strategy"] == StrategyProfile.ADVERSARIAL.value
    assert len(result["day_history"]) == 10
    assert snapshot["event_count"] > 0
    assert snapshot["shipments"]


def test_m8_same_seed_same_strategy_is_deterministic() -> None:
    first = IntegratedV01Engine.new(805)
    second = IntegratedV01Engine.new(805)

    first_snapshot = first.run_to_day(StrategyProfile.COOPERATIVE, 10)
    second_snapshot = second.run_to_day(StrategyProfile.COOPERATIVE, 10)

    assert first_snapshot == second_snapshot
    assert [event.to_dict() for event in first.world.event_log] == [
        event.to_dict() for event in second.world.event_log
    ]


def test_m8_save_resume_mid_run_matches_uninterrupted(tmp_path: Path) -> None:
    seed = 806
    uninterrupted = IntegratedV01Engine.new(seed)
    uninterrupted_snapshot = uninterrupted.run_to_day(StrategyProfile.COOPERATIVE, 10)

    split = IntegratedV01Engine.new(seed)
    split.run_to_day(StrategyProfile.COOPERATIVE, 5)
    save_path = tmp_path / "v01-mid-run.json"
    split.save(save_path)

    resumed = IntegratedV01Engine.load(save_path)
    resumed_snapshot = resumed.run_to_day(StrategyProfile.COOPERATIVE, 10)

    assert resumed_snapshot == uninterrupted_snapshot
    assert [event.to_dict() for event in resumed.world.event_log] == [
        event.to_dict() for event in uninterrupted.world.event_log
    ]


def test_m8_same_seed_strategies_materially_diverge() -> None:
    result = run_v01_comparison(807)
    divergence = result["divergence"]

    assert divergence["passes"]
    assert divergence["different_count"] >= 13

    required = {
        "wealth",
        "cultivation",
        "gu_condition",
        "killer_move",
        "relationships",
        "npc_goals",
        "markets",
        "resource_nodes",
        "shipment",
        "belief_chain",
        "faction_case",
        "standings",
        "membership_or_access",
    }
    assert all(divergence["dimensions"][name] for name in required)


def test_m8_remote_world_acts_without_player_input() -> None:
    engine = IntegratedV01Engine.new(808)
    before = sum(state.action_count for state in engine.remote_actors.values())

    engine.advance_seconds(48 * 3_600)

    after = sum(state.action_count for state in engine.remote_actors.values())
    assert after > before
    assert any(
        event.event_type == "M8_REMOTE_NPC_ACTION"
        for event in engine.world.event_log
    )
