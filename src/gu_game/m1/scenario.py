"""Deterministic scripted Day 1~2 scenario used by the CLI and CI smoke."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import ActionIntent, ActionType
from .simulation import Simulation


def prepare_day_one(simulation: Simulation) -> None:
    player_id = simulation.player_id
    simulation.execute(
        ActionIntent(ActionType.GATHER, player_id, resource_id=simulation.FOOD_RESOURCE_ID, quantity=6)
    )
    simulation.execute(
        ActionIntent(ActionType.SELL, player_id, resource_id=simulation.FOOD_RESOURCE_ID, quantity=1)
    )
    simulation.execute(
        ActionIntent(ActionType.BUY, player_id, resource_id=simulation.FOOD_RESOURCE_ID, quantity=2)
    )
    simulation.execute(
        ActionIntent(ActionType.WAIT, player_id, duration_seconds=6 * 3_600)
    )


def finish_day_two(simulation: Simulation) -> None:
    player_id = simulation.player_id
    player = simulation.characters[player_id]
    simulation.execute(ActionIntent(ActionType.FEED_GU, player_id, gu_id=player.owned_gu_ids[0]))
    simulation.execute(ActionIntent(ActionType.CULTIVATE, player_id))
    simulation.execute(
        ActionIntent(
            ActionType.WAIT,
            player_id,
            duration_seconds=14 * 3_600,
        )
    )


def run_day1_day2(seed: int = 20260925, save_path: str | Path | None = None) -> Simulation:
    simulation = Simulation.new(seed)
    prepare_day_one(simulation)
    if save_path is not None:
        simulation.save(str(save_path))
    finish_day_two(simulation)
    return simulation


def run_and_summarize(seed: int = 20260925) -> dict[str, Any]:
    simulation = run_day1_day2(seed)
    return {
        "summary": simulation.summary(),
        "event_log_tail": simulation.event_log_tail(),
    }
