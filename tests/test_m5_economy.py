from __future__ import annotations

from pathlib import Path

from gu_game.m5.engine import EconomyLogisticsEngine
from gu_game.m5.models import ShipmentStatus


def test_m5_bootstrap_has_finite_content_and_market_divergence() -> None:
    engine = EconomyLogisticsEngine.new(101)
    assert len(engine.nodes) == 20
    assert len(engine.MARKET_IDS) == 3
    assert len(engine.routes) == 6
    assert len(engine.simulation.resource_definitions) >= 40
    prices = [engine.simulation.markets[mid].price_for(engine.resource_groups["food"][0]) for mid in engine.MARKET_IDS]
    assert len(set(prices)) > 1


def test_overharvest_damages_health_and_regenerates() -> None:
    engine = EconomyLogisticsEngine.new(102)
    node_id = "resource-node-m5-01"
    before_health = engine.nodes[node_id].health
    before_stock = engine.simulation.resource_nodes[node_id].current_stock
    resource_id = engine.simulation.resource_nodes[node_id].resource_definition_id
    lots = engine.gather(engine.simulation.player_id, node_id, 8)
    assert lots[0].definition_id == resource_id
    assert engine.nodes[node_id].health < before_health
    assert engine.simulation.resource_nodes[node_id].current_stock < before_stock
    engine.advance_time(3_600, run_npcs=False)
    assert engine.simulation.resource_nodes[node_id].current_stock > before_stock - 8


def test_actual_cargo_moves_and_procurement_updates_faction() -> None:
    engine = EconomyLogisticsEngine.new(103)
    origin = engine.simulation.markets[engine.MARKET_IDS[0]]
    resource_id = next(item for item in engine.resource_groups["food"] if origin.inventory_quantity(item) >= 2)
    before = origin.inventory_quantity(resource_id)
    shipment = engine.procure_for_faction("faction-river-traders", resource_id, 2, guards=3)
    assert shipment.status is ShipmentStatus.IN_TRANSIT
    assert origin.inventory_quantity(resource_id) == before - 2
    engine.advance_time(2 * 3_600, run_npcs=False)
    assert shipment.status is ShipmentStatus.ARRIVED
    faction = engine.factions["faction-river-traders"]
    assert sum(lot.quantity for lot in faction.warehouse.values()) >= 2


def test_save_resume_in_transit_is_deterministic(tmp_path: Path) -> None:
    engine = EconomyLogisticsEngine.new(104)
    origin = engine.simulation.markets[engine.MARKET_IDS[0]]
    resource_id = next(item for item in engine.resource_groups["food"] if origin.inventory_quantity(item) >= 2)
    shipment = engine.dispatch(engine.simulation.player_id, "route-grove-river", resource_id, 2, guards=3)
    path = tmp_path / "m5-save.json"
    engine.save(path)
    resumed = EconomyLogisticsEngine.load(path)
    engine.advance_time(2 * 3_600, run_npcs=False)
    resumed.advance_time(2 * 3_600, run_npcs=False)
    assert engine.shipments[shipment.shipment_id].status is resumed.shipments[shipment.shipment_id].status
    assert engine.summary() == resumed.summary()
    assert [event.to_dict() for event in engine.world.event_log] == [event.to_dict() for event in resumed.world.event_log]


def test_shortage_changes_goals_without_creating_inventory() -> None:
    engine = EconomyLogisticsEngine.new(105)
    market_id = engine.MARKET_IDS[1]
    food_id = engine.resource_groups["food"][0]
    market = engine.simulation.markets[market_id]
    for lot_id in list(market.inventory):
        if market.inventory[lot_id].definition_id == food_id:
            del market.inventory[lot_id]
    engine.demand[market_id][food_id] = 20
    engine.refresh_shortages()
    assert engine.shortages[f"{market_id}:{food_id}"].active
    assert any(goal in {"SECURE_GU_FOOD", "SEEK_SUBSTITUTE"} for goal in engine.npc_goals.values())
    assert market.inventory_quantity(food_id) == 0
