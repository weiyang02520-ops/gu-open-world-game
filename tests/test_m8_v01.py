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

    kinds = [location.kind for location in engine.locations.values()]
    assert kinds.count("MAIN_SETTLEMENT") == 1
    assert 2 <= kinds.count("SMALL_SETTLEMENT") <= 4
    assert kinds.count("RESOURCE_AREA") >= 5
    assert any(kind in {"ROUTE", "DANGER_ROUTE", "ROUTE_STOP"} for kind in kinds)
    assert all(
        location.neighbors
        for location in engine.locations.values()
        if location.kind not in {"TRAINING", "MARKET_WARD", "FACTION_HQ"}
    )


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
    missing = sorted(
        name for name in required if not divergence["dimensions"][name]
    )
    assert not missing, (
        f"required V0.1 divergence dimensions did not change: {missing}; "
        f"all dimensions={divergence['dimensions']}"
    )


    cooperative = result["cooperative"]
    adversarial = result["adversarial"]

    relationship_differences = sum(
        cooperative["relationships"].get(npc_id)
        != adversarial["relationships"].get(npc_id)
        for npc_id in set(cooperative["relationships"]) | set(adversarial["relationships"])
    )
    goal_differences = sum(
        cooperative["npc_goals"].get(npc_id)
        != adversarial["npc_goals"].get(npc_id)
        for npc_id in set(cooperative["npc_goals"]) | set(adversarial["npc_goals"])
    )
    market_differences = sum(
        cooperative["markets"].get(market_id)
        != adversarial["markets"].get(market_id)
        for market_id in set(cooperative["markets"]) | set(adversarial["markets"])
    )
    node_differences = sum(
        cooperative["resource_nodes"].get(node_id)
        != adversarial["resource_nodes"].get(node_id)
        for node_id in set(cooperative["resource_nodes"]) | set(adversarial["resource_nodes"])
    )
    standing_differences = sum(
        cooperative["standings"].get(faction_id)
        != adversarial["standings"].get(faction_id)
        for faction_id in set(cooperative["standings"]) | set(adversarial["standings"])
    )

    assert relationship_differences >= 3
    assert goal_differences >= 2
    assert market_differences >= 2
    assert node_differences >= 2
    assert standing_differences >= 2


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
    assert any(
        event.event_type == "M6_ABSTRACT_CULTIVATION_SESSION"
        for event in engine.world.event_log
    )


def test_m8_mission_lifecycle_player_ignore_and_npc_completion() -> None:
    engine = IntegratedV01Engine.new(809)
    snapshot = engine.run_to_day(StrategyProfile.COOPERATIVE, 10)

    player_mission_id = engine.flags["player_mission_id"]
    ignored_mission_id = engine.flags["ignored_mission_id"]
    npc_mission_id = engine.flags["npc_mission_id"]

    assert snapshot["missions"][player_mission_id]["status"] == "COMPLETED"
    assert snapshot["missions"][npc_mission_id]["status"] == "COMPLETED"
    assert snapshot["missions"][ignored_mission_id]["status"] == "EXPIRED"
    assert snapshot["missions"][npc_mission_id]["assignee_id"] in engine.simulation.npc_ids


def test_m8_factions_evolve_during_48h_player_idle() -> None:
    engine = IntegratedV01Engine.new(810)

    grove = "faction-grove-watch"
    river = "faction-river-traders"
    grove_mission = engine.factions.generate_mission(
        grove,
        engine._issuer_for(grove, "ISSUE_MISSION"),
        "WATCH_TARGET",
        target_id=engine.simulation.player_id,
    )
    river_mission = engine.factions.generate_mission(
        river,
        engine._issuer_for(river, "ISSUE_MISSION"),
        "GATHER",
        target_id=engine.simulation.FOOD_RESOURCE_ID,
    )

    need_updates_before = {
        key: need.updated_at for key, need in engine.factions.needs.items()
    }
    engine.advance_seconds(48 * 3_600)

    assert engine.factions.missions[grove_mission.mission_id].status == "EXPIRED"
    assert engine.factions.missions[river_mission.mission_id].status == "EXPIRED"
    assert all(
        need.updated_at >= need_updates_before[key]
        for key, need in engine.factions.needs.items()
    )
    expired_factions = {
        event.payload["faction_id"]
        for event in engine.world.event_log
        if event.event_type == "FACTION_MISSION_EXPIRED"
    }
    assert {grove, river}.issubset(expired_factions)


def test_m8_same_identity_can_have_different_faction_standings() -> None:
    cooperative = IntegratedV01Engine.new(811)
    snapshot = cooperative.run_to_day(StrategyProfile.COOPERATIVE, 5)

    assert len(snapshot["standings"]) >= 3
    assert len(set(snapshot["standings"].values())) >= 2


def test_m8_event_log_explains_strategy_divergence() -> None:
    result = run_v01_comparison(812)
    cooperative_events = result["cooperative"]["event_types"]
    adversarial_events = result["adversarial"]["event_types"]

    assert cooperative_events.get("M8_SUPPLY_MISSION_DELIVERED", 0) >= 1
    assert cooperative_events.get("M5_SHIPMENT_ARRIVED", 0) >= 1

    assert adversarial_events.get("M8_MARKET_THEFT", 0) >= 1
    assert adversarial_events.get("M8_SHIPMENT_ROBBED", 0) >= 1

    # Both strategies still pass through the same systemic domains, but the
    # causal event chains differ because the chosen actions differ.
    assert cooperative_events != adversarial_events
