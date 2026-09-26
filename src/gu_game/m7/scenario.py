"""M7 Effect Graph / killer-move smoke scenario."""

from __future__ import annotations

from typing import Any

from ..m6.models import InsightType
from .engine import EffectGraphEngine


def run_m7_smoke(seed: int = 20260925) -> dict[str, Any]:
    engine = EffectGraphEngine.new(seed)
    player_id = engine.simulation.player_id
    target_id = engine.simulation.npc_ids[0]

    # Give enough varied insight to prove high attainment permits a three-Gu move.
    engine.cultivation.gain_insight(
        player_id,
        "path-movement",
        insight_type=InsightType.EXPERIMENTATION,
        source_key="m7-composite-design",
        base_value=200,
    )
    gu_ids = list(engine.simulation.characters[player_id].owned_gu_ids[:3])
    move = engine.design_killer_move(
        player_id, "Threefold Ash Step", gu_ids, "path-movement"
    )

    # Research consumes a real M5 refinement lot.
    engine.cultivation.economy.buy(
        player_id, "market-ash-camp", "resource-refine-01", 2
    )
    engine.research_killer_move(move.instance_id)
    engine.research_killer_move(move.instance_id)

    encounter = engine.combat.start_encounter(
        (player_id, target_id), positions={player_id: 0, target_id: 8}
    )
    essence_before = engine.simulation.characters[player_id].cultivation.primeval_current
    result = engine.execute_killer_move(
        move.instance_id, encounter.encounter_id, player_id, target_id
    )
    target_body = encounter.actors[target_id].body.summary()

    return {
        "phase": "M7",
        "seed": seed,
        "killer_move": engine.summary(player_id)["killer_moves"][0],
        "execution": result.to_dict(),
        "essence_before": essence_before,
        "essence_after": engine.simulation.characters[player_id].cultivation.primeval_current,
        "positions": {key: value.position for key, value in encounter.actors.items()},
        "target_body": target_body,
        "event_log_tail": [event.to_dict() for event in engine.world.event_log[-18:]],
    }
