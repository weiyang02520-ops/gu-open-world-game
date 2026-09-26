from __future__ import annotations

from pathlib import Path

import pytest

from gu_game.m6.models import InsightType
from gu_game.m7.engine import EffectGraphEngine, EffectGraphValidationError
from gu_game.m7.models import EffectGraph, KillerMoveMastery


def _player_gu(engine: EffectGraphEngine) -> list[str]:
    return list(engine.simulation.characters[engine.simulation.player_id].owned_gu_ids)


def test_legacy_m2_profiles_have_serializable_effect_graphs() -> None:
    engine = EffectGraphEngine.new(301)
    assert len(engine.profile_graphs) == len(engine.combat.profiles)
    graph = engine.graphs[next(iter(engine.profile_graphs.values()))]
    assert EffectGraph.from_dict(graph.to_dict()).to_dict() == graph.to_dict()


def test_attainment_controls_killer_move_complexity() -> None:
    engine = EffectGraphEngine.new(302)
    player_id = engine.simulation.player_id
    gu_ids = _player_gu(engine)[:3]
    with pytest.raises(EffectGraphValidationError):
        engine.design_killer_move(player_id, "Too Complex", gu_ids, "path-movement")
    engine.cultivation.gain_insight(
        player_id, "path-movement",
        insight_type=InsightType.EXPERIMENTATION,
        source_key="complexity-breakthrough", base_value=90,
    )
    move = engine.design_killer_move(
        player_id, "Three Gu Prototype", gu_ids, "path-movement"
    )
    assert engine.definitions[move.definition_id].complexity == 3


def test_research_consumes_real_material_and_improves_stability() -> None:
    engine = EffectGraphEngine.new(303)
    player_id = engine.simulation.player_id
    gu_ids = _player_gu(engine)[:2]
    move = engine.design_killer_move(
        player_id, "Two Gu Prototype", gu_ids, "path-movement"
    )
    before = engine.effective_stability(move.instance_id)
    engine.cultivation.economy.buy(
        player_id, "market-ash-camp", "resource-refine-01", 1
    )
    material_before = engine.simulation.characters[player_id].inventory_quantity(
        "resource-refine-01"
    )
    engine.research_killer_move(move.instance_id)
    material_after = engine.simulation.characters[player_id].inventory_quantity(
        "resource-refine-01"
    )
    assert material_after == material_before - 1
    assert engine.effective_stability(move.instance_id) > before
    assert move.research_count == 1
    assert move.mastery in {
        KillerMoveMastery.USABLE,
        KillerMoveMastery.PROFICIENT,
        KillerMoveMastery.MASTERED,
    }


def test_mature_killer_move_executes_effect_graph_in_combat() -> None:
    engine = EffectGraphEngine.new(304)
    player_id = engine.simulation.player_id
    target_id = engine.simulation.npc_ids[0]
    engine.cultivation.gain_insight(
        player_id, "path-movement",
        insight_type=InsightType.EXPERIMENTATION,
        source_key="master-composition", base_value=200,
    )
    move = engine.design_killer_move(
        player_id, "Threefold Step", _player_gu(engine)[:3], "path-movement"
    )
    engine.cultivation.economy.buy(
        player_id, "market-ash-camp", "resource-refine-01", 2
    )
    engine.research_killer_move(move.instance_id)
    engine.research_killer_move(move.instance_id)
    assert engine.effective_stability(move.instance_id) >= 95
    encounter = engine.combat.start_encounter(
        (player_id, target_id), positions={player_id: 0, target_id: 8}
    )
    essence_before = engine.simulation.characters[player_id].cultivation.primeval_current
    result = engine.execute_killer_move(
        move.instance_id, encounter.encounter_id, player_id, target_id
    )
    assert result.success
    assert result.executed_nodes
    assert engine.simulation.characters[player_id].cultivation.primeval_current < essence_before
    assert encounter.actors[player_id].position != 0
    assert encounter.actors[target_id].body.injuries


def test_extremely_unstable_move_backlashes_and_strains_gu() -> None:
    engine = EffectGraphEngine.new(305)
    player_id = engine.simulation.player_id
    target_id = engine.simulation.npc_ids[0]
    move = engine.design_killer_move(
        player_id, "Broken Prototype", _player_gu(engine)[:2], "path-movement"
    )
    move.stability_modifier = -100
    component_ids = (
        engine.definitions[move.definition_id].core_gu_ids
        + engine.definitions[move.definition_id].auxiliary_gu_ids
    )
    condition_before = {
        gu_id: engine.simulation.gu_instances[gu_id].condition for gu_id in component_ids
    }
    encounter = engine.combat.start_encounter(
        (player_id, target_id), positions={player_id: 0, target_id: 4}
    )
    result = engine.execute_killer_move(
        move.instance_id, encounter.encounter_id, player_id, target_id
    )
    assert not result.success
    assert result.backlash
    assert encounter.actors[player_id].body.injuries
    assert all(
        engine.simulation.gu_instances[gu_id].condition < condition_before[gu_id]
        for gu_id in component_ids
    )


def test_m7_save_resume_preserves_graphs_and_research(tmp_path: Path) -> None:
    engine = EffectGraphEngine.new(306)
    player_id = engine.simulation.player_id
    move = engine.design_killer_move(
        player_id, "Saved Prototype", _player_gu(engine)[:2], "path-movement"
    )
    engine.cultivation.economy.buy(
        player_id, "market-ash-camp", "resource-refine-01", 1
    )
    engine.research_killer_move(move.instance_id)
    path = tmp_path / "m7-save.json"
    engine.save(path)
    resumed = EffectGraphEngine.load(path)
    assert engine.to_dict() == resumed.to_dict()
    assert engine.summary() == resumed.summary()
    assert [event.to_dict() for event in engine.world.event_log] == [
        event.to_dict() for event in resumed.world.event_log
    ]
