"""M5 resource-crisis smoke scenarios used by CI and the CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .engine import EconomyLogisticsEngine
from .models import ShipmentStatus


def run_m5_smoke(seed: int = 20260925) -> dict[str, Any]:
    engine = EconomyLogisticsEngine.new(seed)
    player_id = engine.simulation.player_id
    node_id = "resource-node-m5-01"
    resource_id = engine.simulation.resource_nodes[node_id].resource_definition_id
    engine.gather(player_id, node_id, 8)

    # Force a visible crisis at the river hub without inventing stock.
    river = engine.simulation.markets[engine.MARKET_IDS[1]]
    for lot_id in list(river.inventory):
        if river.inventory[lot_id].definition_id in engine.resource_groups["food"]:
            del river.inventory[lot_id]
    engine.demand[engine.MARKET_IDS[1]][engine.resource_groups["food"][0]] = 16
    engine.refresh_shortages(force=True)

    # Actual cargo leaves the source market and remains in transit in the smoke.
    origin = engine.simulation.markets[engine.MARKET_IDS[0]]
    cargo_resource = next(
        resource_id for resource_id in engine.resource_groups["food"]
        if origin.inventory_quantity(resource_id) >= 2
    )
    shipment = engine.procure_for_faction(
        "faction-river-traders", cargo_resource, 2, route_id="route-grove-river", guards=3
    )
    in_transit = shipment.status is ShipmentStatus.IN_TRANSIT
    engine.advance_time(2 * 3_600, run_npcs=False)
    resolved = engine.shipments[shipment.shipment_id]
    return {
        "phase": "M5",
        "seed": seed,
        "resource_id_gathered": resource_id,
        "in_transit_before_advance": in_transit,
        "shipment_status": resolved.status.value,
        "cargo_quantity": sum(max(0, lot.quantity) for lot in resolved.cargo),
        "npc_goals": dict(engine.npc_goals),
        "summary": engine.summary(),
        "event_log_tail": [event.to_dict() for event in engine.world.event_log[-12:]],
    }


def save_resume_m5(path: str | Path, seed: int = 20260925) -> tuple[dict[str, Any], dict[str, Any]]:
    engine = EconomyLogisticsEngine.new(seed)
    origin = engine.simulation.markets[engine.MARKET_IDS[0]]
    resource_id = next(
        resource_id for resource_id in engine.resource_groups["food"]
        if origin.inventory_quantity(resource_id) >= 2
    )
    shipment = engine.dispatch(engine.simulation.player_id, "route-grove-river", resource_id, 2, guards=3)
    engine.save(path)
    resumed = EconomyLogisticsEngine.load(path)
    resumed.advance_time(2 * 3_600, run_npcs=False)
    return (
        {"shipment_id": shipment.shipment_id, "status": shipment.status.value},
        {"shipment_id": resumed.shipments[shipment.shipment_id].shipment_id,
         "status": resumed.shipments[shipment.shipment_id].status.value,
         "snapshot": resumed.summary()},
    )
