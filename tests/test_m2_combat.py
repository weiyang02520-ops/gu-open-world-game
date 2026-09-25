from pathlib import Path

from gu_game.m1.simulation import Simulation
from gu_game.m2.balance import GAME_EXTENSION_COMBAT_BALANCE as B
from gu_game.m2.engine import CombatEngine
from gu_game.m2.models import BodyPart, CombatGuRole, CombatStatus
from gu_game.m2.scenario import (
    scenario_attack_lands,
    scenario_detected_evade,
    scenario_npc_retreat,
)


def _types(engine: CombatEngine) -> list[str]:
    return [event.event_type for event in engine.world.event_log]


def test_detected_attack_can_be_evaded_before_resolution() -> None:
    engine, encounter_id = scenario_detected_evade(20260925)
    summary = engine.summary(encounter_id)

    defender = engine.encounters[encounter_id].participants[1]
    assert summary["status"] == CombatStatus.ACTIVE.value
    assert summary["actors"][defender]["injuries"] == []
    assert abs(summary["positions"][engine.encounters[encounter_id].participants[0]] - summary["positions"][defender]) > B["attack_range"]
    assert "THREAT_PERCEIVED" in _types(engine)
    assert "ATTACK_EVADED" in _types(engine)
    assert engine.world.clock.elapsed_seconds == 1


def test_attack_lands_as_concrete_leg_injury_and_changes_movement() -> None:
    engine, encounter_id = scenario_attack_lands(20260925)
    encounter = engine.encounters[encounter_id]
    attacker, defender = encounter.participants
    summary = engine.summary(encounter_id)
    injuries = summary["actors"][defender]["injuries"]

    assert injuries
    assert injuries[0]["part"] == BodyPart.LEFT_LEG.value
    assert injuries[0]["severity"] == "HEAVY"
    assert summary["actors"][defender]["movement_distance"] < B["movement_distance"]
    assert "INJURY_APPLIED" in _types(engine)

    # The injured leg reduces a later flee distance from 12 to 10 units.
    engine.declare_flee(
        encounter_id,
        defender,
        attacker,
        engine.profile_for_role(defender, CombatGuRole.MOVEMENT).profile_id,
    )
    engine.advance_ticks(encounter_id, 1)
    assert engine.summary(encounter_id)["positions"][defender] == 14
    assert engine.summary(encounter_id)["status"] == CombatStatus.DISENGAGED.value


def test_perceived_state_does_not_expose_hidden_target_essence() -> None:
    simulation = Simulation.new(20260925)
    engine = CombatEngine.new(simulation)
    npc, player = simulation.npc_ids[0], simulation.player_id
    encounter = engine.start_encounter((npc, player), positions={npc: 0, player: 4})

    snapshot = engine.perceived_snapshot(encounter.encounter_id, npc, player)
    data = snapshot.to_dict()
    assert "target_essence" not in data
    assert "target_primeval_current" not in data
    decision = engine.choose_npc_action(encounter.encounter_id, npc, player)
    assert decision.snapshot.to_dict() == data


def test_npc_can_choose_flee_from_visible_risk_and_disengage() -> None:
    engine, encounter_id = scenario_npc_retreat(20260925)
    summary = engine.summary(encounter_id)

    assert summary["status"] == CombatStatus.DISENGAGED.value
    assert summary["exit_reason"] == "flee_success"
    decisions = [event for event in engine.world.event_log if event.event_type == "NPC_COMBAT_DECISION"]
    assert decisions
    assert decisions[-1].payload["decision"] == "FLEE"


def test_detected_but_insufficient_essence_cannot_react() -> None:
    simulation = Simulation.new(20260925)
    engine = CombatEngine.new(simulation)
    attacker, defender = simulation.npc_ids[0], simulation.player_id
    encounter = engine.start_encounter((attacker, defender), positions={attacker: 0, defender: 4})
    engine.activate_perception(
        encounter.encounter_id,
        defender,
        engine.profile_for_role(defender, CombatGuRole.PERCEPTION).profile_id,
    )
    engine.declare_attack(
        encounter.encounter_id,
        attacker,
        defender,
        engine.profile_for_role(attacker, CombatGuRole.ATTACK).profile_id,
    )
    simulation.characters[defender].cultivation.primeval_current = 0
    result = engine.select_reaction(
        encounter.encounter_id,
        defender,
        engine.profile_for_role(defender, CombatGuRole.MOVEMENT).profile_id,
    )
    assert not result.success
    assert result.reason == "insufficient_essence"
    engine.advance_ticks(encounter.encounter_id, 4)
    assert engine.summary(encounter.encounter_id)["actors"][defender]["injuries"]


def test_active_combat_save_resume_matches_uninterrupted(tmp_path: Path) -> None:
    simulation = Simulation.new(20260925)
    engine = CombatEngine.new(simulation)
    attacker, defender = simulation.npc_ids[0], simulation.player_id
    encounter = engine.start_encounter((attacker, defender), positions={attacker: 0, defender: 4})
    engine.declare_attack(
        encounter.encounter_id,
        attacker,
        defender,
        engine.profile_for_role(attacker, CombatGuRole.ATTACK).profile_id,
    )
    engine.advance_ticks(encounter.encounter_id, 2)
    checkpoint = tmp_path / "active-combat.json"
    engine.save(checkpoint)

    engine.advance_ticks(encounter.encounter_id, 2)
    uninterrupted_state = engine.to_dict()
    uninterrupted_events = [event.to_dict() for event in engine.world.event_log]

    resumed = CombatEngine.load(checkpoint)
    resumed.advance_ticks(encounter.encounter_id, 2)
    assert resumed.to_dict() == uninterrupted_state
    assert [event.to_dict() for event in resumed.world.event_log] == uninterrupted_events


def test_same_seed_combat_events_are_reproducible() -> None:
    first, first_id = scenario_detected_evade(20260925)
    second, second_id = scenario_detected_evade(20260925)

    assert first.to_dict() == second.to_dict()
    assert first.summary(first_id) == second.summary(second_id)
    assert [event.to_dict() for event in first.world.event_log] == [
        event.to_dict() for event in second.world.event_log
    ]


def test_m1_save_without_combat_state_remains_loadable(tmp_path: Path) -> None:
    simulation = Simulation.new(20260925)
    path = tmp_path / "m1-save.json"
    simulation.save(path)
    restored = Simulation.load(path)

    assert restored.summary() == simulation.summary()
    assert "m2_combat" not in restored.world.game_state
