"""Deterministic M2 combat scenarios used by tests, CLI and CI smoke."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..m1.simulation import Simulation
from .engine import CombatEngine
from .models import CombatGuRole


def _participants(simulation: Simulation) -> tuple[str, str]:
    return simulation.npc_ids[0], simulation.player_id


def scenario_detected_evade(seed: int = 20260925) -> tuple[CombatEngine, str]:
    simulation = Simulation.new(seed)
    engine = CombatEngine.new(simulation)
    attacker, defender = _participants(simulation)
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
    engine.select_reaction(
        encounter.encounter_id,
        defender,
        engine.profile_for_role(defender, CombatGuRole.MOVEMENT).profile_id,
    )
    engine.advance_ticks(encounter.encounter_id, 4)
    return engine, encounter.encounter_id


def scenario_attack_lands(seed: int = 20260925) -> tuple[CombatEngine, str]:
    simulation = Simulation.new(seed)
    engine = CombatEngine.new(simulation)
    attacker, defender = _participants(simulation)
    encounter = engine.start_encounter((attacker, defender), positions={attacker: 0, defender: 4})
    engine.declare_attack(
        encounter.encounter_id,
        attacker,
        defender,
        engine.profile_for_role(attacker, CombatGuRole.ATTACK).profile_id,
    )
    engine.advance_ticks(encounter.encounter_id, 4)
    return engine, encounter.encounter_id


def scenario_npc_retreat(seed: int = 20260925) -> tuple[CombatEngine, str]:
    simulation = Simulation.new(seed)
    engine = CombatEngine.new(simulation)
    npc, player = _participants(simulation)
    simulation.characters[npc].cultivation.primeval_current = 18
    engine.npc_risk_tolerance[npc] = 10
    encounter = engine.start_encounter((npc, player), positions={npc: 0, player: 4})
    engine.declare_attack(
        encounter.encounter_id,
        player,
        npc,
        engine.profile_for_role(player, CombatGuRole.ATTACK).profile_id,
    )
    decision = engine.run_npc_decision(encounter.encounter_id, npc, player)
    assert decision.decision.value == "FLEE"
    engine.advance_ticks(encounter.encounter_id, 4)
    return engine, encounter.encounter_id


def run_m2_smoke(seed: int = 20260925) -> dict[str, Any]:
    evade_engine, evade_id = scenario_detected_evade(seed)
    land_engine, land_id = scenario_attack_lands(seed)
    retreat_engine, retreat_id = scenario_npc_retreat(seed)
    return {
        "detected_evade": evade_engine.summary(evade_id),
        "attack_lands": land_engine.summary(land_id),
        "npc_retreat": retreat_engine.summary(retreat_id),
    }


def save_resume_mid_combat(path: str | Path, seed: int = 20260925) -> tuple[CombatEngine, str]:
    # Build a fresh active encounter so the checkpoint is genuinely mid-combat.
    simulation = Simulation.new(seed)
    engine = CombatEngine.new(simulation)
    attacker, defender = _participants(simulation)
    encounter = engine.start_encounter((attacker, defender), positions={attacker: 0, defender: 4})
    engine.declare_attack(
        encounter.encounter_id,
        attacker,
        defender,
        engine.profile_for_role(attacker, CombatGuRole.ATTACK).profile_id,
    )
    engine.advance_ticks(encounter.encounter_id, 2)
    engine.save(path)
    return engine, encounter.encounter_id
