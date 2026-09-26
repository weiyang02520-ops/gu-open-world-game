"""Final V0.1 Day1-10 smoke and divergence scenarios."""

from __future__ import annotations

from typing import Any

from .engine import IntegratedV01Engine
from .models import StrategyProfile


def run_v01_smoke(
    seed: int = 20260925,
    strategy: StrategyProfile | str = StrategyProfile.COOPERATIVE,
) -> dict[str, Any]:
    """Run one complete deterministic Day1-10 strategy."""

    strategy = StrategyProfile(strategy)
    engine = IntegratedV01Engine.new(seed)
    snapshot = engine.run_to_day(strategy, 10)
    return {
        "phase": "V0.1",
        "seed": seed,
        "strategy": strategy.value,
        "snapshot": snapshot,
        "day_history": list(engine.day_history),
        "event_log_tail": [
            event.to_dict() for event in engine.world.event_log[-20:]
        ],
    }


def run_v01_comparison(seed: int = 20260925) -> dict[str, Any]:
    """Run both final strategies from the same seed and compare world states."""

    cooperative_engine = IntegratedV01Engine.new(seed)
    cooperative = cooperative_engine.run_to_day(StrategyProfile.COOPERATIVE, 10)

    adversarial_engine = IntegratedV01Engine.new(seed)
    adversarial = adversarial_engine.run_to_day(StrategyProfile.ADVERSARIAL, 10)

    divergence = IntegratedV01Engine.divergence_report(cooperative, adversarial)
    return {
        "phase": "V0.1_COMPARE",
        "seed": seed,
        "cooperative": cooperative,
        "adversarial": adversarial,
        "divergence": divergence,
        "cooperative_event_tail": [
            event.to_dict() for event in cooperative_engine.world.event_log[-12:]
        ],
        "adversarial_event_tail": [
            event.to_dict() for event in adversarial_engine.world.event_log[-12:]
        ],
    }
