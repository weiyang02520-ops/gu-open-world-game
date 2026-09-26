from __future__ import annotations

from pathlib import Path

import pytest

from gu_game.m5.models import ShipmentStatus
from gu_game.m6.engine import CultivationAttainmentEngine, CultivationValidationError
from gu_game.m6.models import BreakthroughMode, InsightType, MinorStage


def test_m6_bootstrap_separates_rank_stage_knowledge_and_attainment() -> None:
    engine = CultivationAttainmentEngine.new(201)
    player = engine.simulation.characters[engine.simulation.player_id]
    assert player.cultivation.rank == 1
    assert player.cultivation.minor_stage == MinorStage.INITIAL.value
    assert set(engine.paths) == {"path-strength", "path-wisdom", "path-movement"}
    assert not [
        item for item in engine.knowledge.values()
        if item.character_id == player.character_id
    ]
    assert engine._attainment(player.character_id, "path-wisdom").insight_points == 0


def test_cultivation_consumes_essence_and_world_continues() -> None:
    engine = CultivationAttainmentEngine.new(202)
    player_id = engine.simulation.player_id
    player = engine.simulation.characters[player_id]
    origin = engine.simulation.markets[engine.economy.MARKET_IDS[0]]
    resource_id = next(
        resource_id for resource_id in engine.economy.resource_groups["food"]
        if origin.inventory_quantity(resource_id) >= 2
    )
    shipment = engine.economy.procure_for_faction(
        "faction-river-traders", resource_id, 2,
        route_id="route-grove-river", guards=3,
    )
    essence_before = player.cultivation.primeval_current
    time_before = engine.world.clock.elapsed_seconds
    engine.cultivate(player_id, hours=3)
    assert player.cultivation.primeval_current < essence_before
    assert player.cultivation.wall_progress > 0
    assert engine.world.clock.elapsed_seconds == time_before + 3 * 3_600
    assert engine.economy.shipments[shipment.shipment_id].status is ShipmentStatus.ARRIVED


def test_safe_breakthrough_advances_stage_and_aptitude_affects_capacity_gain() -> None:
    engine = CultivationAttainmentEngine.new(203)
    player_id = engine.simulation.player_id
    player = engine.simulation.characters[player_id]
    before_capacity = player.cultivation.aperture_capacity
    engine.cultivate(player_id, hours=9, method_id="method-deep-circulation")
    engine.cultivate(player_id, hours=1, method_id="method-deep-circulation")
    assert engine.profiles[player_id].breakthrough_ready
    result = engine.attempt_breakthrough(player_id, BreakthroughMode.SAFE)
    assert result.success
    assert result.stage_before is MinorStage.INITIAL
    assert result.stage_after is MinorStage.MIDDLE
    assert player.cultivation.minor_stage == MinorStage.MIDDLE.value
    assert player.cultivation.aperture_capacity > before_capacity
    assert player.cultivation.wall_progress == 0


def test_forced_breakthrough_is_available_earlier_and_deterministic() -> None:
    first = CultivationAttainmentEngine.new(204)
    second = CultivationAttainmentEngine.new(204)
    for engine in (first, second):
        player = engine.simulation.characters[engine.simulation.player_id]
        player.cultivation.wall_progress = (
            player.cultivation.wall_threshold * 70 // 100
        )
    with pytest.raises(CultivationValidationError):
        first.attempt_breakthrough(first.simulation.player_id, BreakthroughMode.SAFE)
    result_a = first.attempt_breakthrough(
        first.simulation.player_id, BreakthroughMode.FORCED
    )
    result_b = second.attempt_breakthrough(
        second.simulation.player_id, BreakthroughMode.FORCED
    )
    assert result_a.to_dict() == result_b.to_dict()
    assert first.summary() == second.summary()
    assert [event.to_dict() for event in first.world.event_log] == [
        event.to_dict() for event in second.world.event_log
    ]


def test_repeated_insight_has_diminishing_novelty_and_knowledge_is_separate() -> None:
    engine = CultivationAttainmentEngine.new(205)
    player_id = engine.simulation.player_id
    first = engine.gain_insight(
        player_id, "path-wisdom",
        insight_type=InsightType.STUDY,
        source_key="same-principle", base_value=30,
    )
    second = engine.gain_insight(
        player_id, "path-wisdom",
        insight_type=InsightType.STUDY,
        source_key="same-principle", base_value=30,
    )
    assert second.awarded_value < first.awarded_value
    assert not engine.knowledge
    study = engine.study(player_id, "source-ash-inscription")
    assert study["knowledge_id"] in engine.knowledge
    assert engine._attainment(player_id, "path-wisdom").insight_points > 0
    assert engine.knowledge[study["knowledge_id"]].subject_id != "path-wisdom"


def test_m6_save_resume_is_deterministic(tmp_path: Path) -> None:
    engine = CultivationAttainmentEngine.new(206)
    player_id = engine.simulation.player_id
    engine.cultivate(player_id, hours=4)
    engine.gain_insight(
        player_id, "path-movement",
        insight_type=InsightType.OBSERVATION,
        source_key="river-current", base_value=16,
    )
    path = tmp_path / "m6-save.json"
    engine.save(path)
    resumed = CultivationAttainmentEngine.load(path)

    engine.rest(player_id, hours=2)
    resumed.rest(player_id, hours=2)
    engine.study(player_id, "source-river-footwork")
    resumed.study(player_id, "source-river-footwork")

    assert engine.summary() == resumed.summary()
    assert engine.to_dict() == resumed.to_dict()
    assert [event.to_dict() for event in engine.world.event_log] == [
        event.to_dict() for event in resumed.world.event_log
    ]
