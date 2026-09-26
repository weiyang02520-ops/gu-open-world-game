"""M6 cultivation/breakthrough/attainment smoke scenario."""

from __future__ import annotations

from typing import Any

from .engine import CultivationAttainmentEngine
from .models import BreakthroughMode, InsightType


def run_m6_smoke(seed: int = 20260925) -> dict[str, Any]:
    engine = CultivationAttainmentEngine.new(seed)
    player_id = engine.simulation.player_id

    origin = engine.simulation.markets[engine.economy.MARKET_IDS[0]]
    cargo_resource = next(
        resource_id
        for resource_id in engine.economy.resource_groups["food"]
        if origin.inventory_quantity(resource_id) >= 2
    )
    shipment = engine.economy.procure_for_faction(
        "faction-river-traders",
        cargo_resource,
        2,
        route_id="route-grove-river",
        guards=3,
    )

    first_session = engine.cultivate(
        player_id, hours=9, method_id="method-deep-circulation"
    )
    second_session = engine.cultivate(
        player_id, hours=1, method_id="method-deep-circulation"
    )
    breakthrough = engine.attempt_breakthrough(player_id, BreakthroughMode.SAFE)

    first_insight = engine.gain_insight(
        player_id,
        "path-wisdom",
        insight_type=InsightType.STUDY,
        source_key="repeatable-principle",
        base_value=20,
    )
    second_insight = engine.gain_insight(
        player_id,
        "path-wisdom",
        insight_type=InsightType.STUDY,
        source_key="repeatable-principle",
        base_value=20,
    )
    study = engine.study(player_id, "source-ash-inscription")

    return {
        "phase": "M6",
        "seed": seed,
        "shipment_status_after_cultivation": engine.economy.shipments[
            shipment.shipment_id
        ].status.value,
        "first_session": first_session,
        "second_session": second_session,
        "breakthrough": breakthrough.to_dict(),
        "repeated_insight_awards": [
            first_insight.awarded_value,
            second_insight.awarded_value,
        ],
        "study": study,
        "summary": engine.summary(player_id),
        "event_log_tail": [
            event.to_dict() for event in engine.world.event_log[-16:]
        ],
    }
