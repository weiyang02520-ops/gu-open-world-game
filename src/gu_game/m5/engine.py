"""Deterministic local economy, shortage and actual-cargo logistics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..m1.models import LocalMarket, ResourceDefinition, ResourceLot, ResourceNode
from ..m1.simulation import ActionValidationError, Simulation
from ..provenance import Provenance
from ..save import load_world, save_world
from .models import (
    Caravan,
    FactionEconomy,
    MarketBelief,
    ResourceNodeCondition,
    RouteDefinition,
    Shipment,
    ShipmentStatus,
    ShortageState,
)


class EconomyLogisticsEngine:
    """M5 layer over the authoritative M1 world and event stream."""

    SCHEMA_VERSION = 1
    MARKET_IDS = ("market-southern-grove", "market-river-crossing", "market-ash-camp")
    FACTION_IDS = ("faction-grove-watch", "faction-river-traders", "faction-ash-study")

    def __init__(self, simulation: Simulation) -> None:
        self.simulation = simulation
        self.world = simulation.world
        self.nodes: dict[str, ResourceNodeCondition] = {}
        self.routes: dict[str, RouteDefinition] = {}
        self.shipments: dict[str, Shipment] = {}
        self.caravans: dict[str, Caravan] = {}
        self.factions: dict[str, FactionEconomy] = {}
        self.market_beliefs: dict[str, MarketBelief] = {}
        self.demand: dict[str, dict[str, int]] = {}
        self.shortages: dict[str, ShortageState] = {}
        self.npc_goals: dict[str, str] = {}
        self.trade_history: list[dict[str, Any]] = []
        saved = self.world.game_state.get("m5_economy")
        if saved:
            self._load_dict(saved)
        else:
            self._bootstrap()
        self._sync_world_state()

    @classmethod
    def new(cls, seed: int) -> "EconomyLogisticsEngine":
        return cls(Simulation.new(seed))

    @classmethod
    def from_simulation(cls, simulation: Simulation) -> "EconomyLogisticsEngine":
        return cls(simulation)

    @classmethod
    def load(cls, path: str | Path) -> "EconomyLogisticsEngine":
        return cls(Simulation.from_world_state(load_world(path)))

    def save(self, path: str | Path) -> Path:
        self._sync_world_state()
        return save_world(self.world, path)

    def _bootstrap(self) -> None:
        self._bootstrap_resources()
        self._bootstrap_markets()
        self._bootstrap_nodes()
        self._bootstrap_routes()
        self._bootstrap_factions()
        self._bootstrap_demand_and_beliefs()
        self._update_all_markets(emit=False)

    def _bootstrap_resources(self) -> None:
        # All catalog entries are original GAME_EXTENSION placeholders.
        groups = {
            "food": [(f"resource-gu-food-{i:02d}", f"Spirit Feed {i:02d}") for i in range(1, 13)],
            "refinement": [(f"resource-refine-{i:02d}", f"Refinement Material {i:02d}") for i in range(1, 23)],
            "ecology": [(f"resource-ecology-{i:02d}", f"Local Ecology Resource {i:02d}") for i in range(1, 13)],
            "strategic": [(f"resource-strategic-{i:02d}", f"Strategic Resource {i:02d}") for i in range(1, 5)],
        }
        all_specs = [spec for specs in groups.values() for spec in specs]
        for definition_id, name in all_specs:
            self.simulation.resource_definitions.setdefault(
                definition_id,
                ResourceDefinition(definition_id, name, base_reference_value=3, provenance="GAME_EXTENSION"),
            )
        # Keep the established M1 food as the first feeding-chain resource.
        self.simulation.resource_definitions[self.simulation.FOOD_RESOURCE_ID].name = "Spirit Grass"
        self.resource_groups = {key: [item[0] for item in specs] for key, specs in groups.items()}

    def _bootstrap_markets(self) -> None:
        market_specs = (
            ("market-river-crossing", "location-river-crossing", 900, 7),
            ("market-ash-camp", "location-ash-camp", 650, 10),
        )
        for market_id, location_id, currency, base_price in market_specs:
            self.simulation.markets.setdefault(
                market_id,
                LocalMarket(
                    market_id=market_id,
                    location_id=location_id,
                    currency=currency,
                    base_prices={key: base_price for key in self.simulation.resource_definitions},
                ),
            )
        for market in self.simulation.markets.values():
            for resource_id in self.simulation.resource_definitions:
                market.base_prices.setdefault(resource_id, 5)
        # Seed finite lots, with different local baskets and stocks.
        seeded = {
            self.MARKET_IDS[0]: (self.resource_groups["food"][:7], 7),
            self.MARKET_IDS[1]: (self.resource_groups["food"][2:10] + self.resource_groups["ecology"][:4], 12),
            self.MARKET_IDS[2]: (self.resource_groups["food"][5:] + self.resource_groups["refinement"][:5], 5),
        }
        for market_id, (resource_ids, quantity) in seeded.items():
            market = self.simulation.markets[market_id]
            for index, resource_id in enumerate(resource_ids):
                if market.inventory_quantity(resource_id):
                    continue
                lot = ResourceLot(
                    self.world.entity_ids.next("lot"), resource_id, quantity + index % 3, 80,
                    market_id, market.location_id,
                )
                market.inventory[lot.lot_id] = lot

    def _bootstrap_nodes(self) -> None:
        definitions = list(self.simulation.resource_definitions)
        market_locations = [self.simulation.markets[key].location_id for key in self.MARKET_IDS]
        # The M1 node is retained and upgraded; 19 more finite nodes make a 20-node region.
        base_node = self.simulation.resource_nodes[self.simulation.RESOURCE_NODE_ID]
        self.nodes[base_node.node_id] = ResourceNodeCondition(base_node.node_id, 100, 100)
        base_node.carrying_capacity = max(base_node.carrying_capacity, 120)
        for index in range(1, 20):
            node_id = f"resource-node-m5-{index:02d}"
            resource_id = definitions[(index * 3) % len(definitions)]
            node = ResourceNode(
                node_id=node_id,
                location_id=f"location-resource-{index:02d}",
                resource_definition_id=resource_id,
                current_stock=18 + index % 9,
                carrying_capacity=30 + index % 12,
                regeneration_per_hour=1 + index % 3,
            )
            self.simulation.resource_nodes[node_id] = node
            self.nodes[node_id] = ResourceNodeCondition(
                node_id=node_id,
                health=75 + index % 26,
                environmental_modifier=75 + (index * 11) % 76,
                controller_id=self.FACTION_IDS[index % len(self.FACTION_IDS)] if index % 4 == 0 else None,
                contested=index % 7 == 0,
                infrastructure=index % 3,
                workers=index % 5,
            )

    def _bootstrap_routes(self) -> None:
        specs = (
            ("route-grove-river", self.MARKET_IDS[0], self.MARKET_IDS[1], 2, 12, 20, 35),
            ("route-river-grove", self.MARKET_IDS[1], self.MARKET_IDS[0], 2, 12, 20, 35),
            ("route-grove-ash", self.MARKET_IDS[0], self.MARKET_IDS[2], 3, 24, 8, 10),
            ("route-ash-grove", self.MARKET_IDS[2], self.MARKET_IDS[0], 3, 24, 8, 10),
            ("route-river-ash", self.MARKET_IDS[1], self.MARKET_IDS[2], 4, 31, 5, 5),
            ("route-ash-river", self.MARKET_IDS[2], self.MARKET_IDS[1], 4, 31, 5, 5),
        )
        for route_id, origin, destination, hours, risk, patrol, control in specs:
            self.routes[route_id] = RouteDefinition(
                route_id, origin, destination, hours, risk, patrol_strength=patrol, faction_control=control
            )

    def _bootstrap_factions(self) -> None:
        for index, faction_id in enumerate(self.FACTION_IDS):
            self.factions[faction_id] = FactionEconomy(
                faction_id=faction_id,
                treasury=180 + index * 40,
                reserves={self.simulation.FOOD_RESOURCE_ID: 8 + index * 2},
            )

    def _bootstrap_demand_and_beliefs(self) -> None:
        for market_index, market_id in enumerate(self.MARKET_IDS):
            self.demand[market_id] = {
                resource_id: (4 + (market_index + resource_index) % 5)
                for resource_index, resource_id in enumerate(self.resource_groups["food"])
            }
            for actor_id in [self.simulation.player_id, *self.simulation.npc_ids]:
                key = self._belief_key(actor_id, market_id)
                self.market_beliefs[key] = MarketBelief(actor_id, market_id)
        for npc_id in self.simulation.npc_ids:
            self.npc_goals[npc_id] = "LOCAL_WORK"

    def gather(self, actor_id: str, node_id: str, quantity: int) -> list[ResourceLot]:
        node = self._node(node_id)
        condition = self.nodes[node_id]
        if quantity <= 0:
            raise ActionValidationError("quantity must be positive")
        if node.current_stock < quantity:
            raise ActionValidationError("resource node does not have enough stock")
        actor = self.simulation._character(actor_id)
        effective_health = max(10, condition.health)
        yield_quantity = max(1, quantity * effective_health // 100)
        node.current_stock -= quantity
        pressure = quantity * 100 // max(1, node.carrying_capacity)
        if pressure >= 20 or quantity >= max(5, node.carrying_capacity // 4):
            condition.health = max(10, condition.health - max(1, quantity // 4))
        node.extraction_pressure += quantity
        lots = [
            ResourceLot(
                self.world.entity_ids.next("lot"), node.resource_definition_id,
                yield_quantity, 70 + condition.health // 10, actor_id, actor.location_id,
                source_node_id=node_id,
            )
        ]
        for lot in lots:
            actor.add_lot(lot)
        self.simulation._emit(
            "M5_RESOURCE_GATHERED", actor_id=actor_id, location_id=node.location_id,
            target_ids=(node_id,), payload={"quantity_removed": quantity, "yield": yield_quantity,
            "health_after": condition.health, "stock_after": node.current_stock,
            "provenance": Provenance.GAME_EXTENSION.value},
        )
        self._sync_world_state()
        return lots

    def buy(self, actor_id: str, market_id: str, resource_id: str, quantity: int) -> int:
        market = self._market(market_id)
        actor = self.simulation._character(actor_id)
        if quantity <= 0 or market.inventory_quantity(resource_id) < quantity:
            raise ActionValidationError("market cannot fulfill requested quantity")
        price = market.price_for(resource_id)
        total = price * quantity
        if actor.currency < total:
            raise ActionValidationError("actor cannot afford purchase")
        moved = self.simulation._take_from_collection(
            market.inventory, resource_id, quantity, owner_id=actor_id, location_id=actor.location_id,
        )
        for lot in moved:
            actor.add_lot(lot)
        actor.currency -= total
        market.currency += total
        market.apply_buy_pressure(resource_id)
        self._record_trade(market_id, actor_id, "BUY", resource_id, quantity, total)
        self._update_market(market_id, resource_id)
        self._emit_trade("MARKET_BUY", market, actor_id, resource_id, quantity, total)
        self._sync_world_state()
        return total

    def sell(self, actor_id: str, market_id: str, resource_id: str, quantity: int) -> int:
        market = self._market(market_id)
        actor = self.simulation._character(actor_id)
        if quantity <= 0 or actor.inventory_quantity(resource_id) < quantity:
            raise ActionValidationError("actor does not own enough resource")
        price = market.price_for(resource_id)
        total = price * quantity
        if market.currency < total:
            raise ActionValidationError("market treasury cannot afford sale")
        moved = self.simulation._take_from_collection(
            actor.inventory, resource_id, quantity, owner_id=market_id, location_id=market.location_id,
        )
        for lot in moved:
            market.inventory[lot.lot_id] = lot
        actor.currency += total
        market.currency -= total
        market.apply_sell_pressure(resource_id)
        self._record_trade(market_id, actor_id, "SELL", resource_id, quantity, total)
        self._update_market(market_id, resource_id)
        self._emit_trade("MARKET_SELL", market, actor_id, resource_id, quantity, total)
        self._sync_world_state()
        return total

    def create_market_belief(self, actor_id: str, market_id: str) -> MarketBelief:
        market = self._market(market_id)
        key = self._belief_key(actor_id, market_id)
        belief = self.market_beliefs.setdefault(key, MarketBelief(actor_id, market_id))
        belief.believed_prices = {
            resource_id: market.price_for(resource_id) for resource_id in market.base_prices
        }
        belief.confidence = min(100, belief.confidence + 15)
        belief.last_observed_at = self.world.clock.elapsed_seconds
        self._sync_world_state()
        return belief

    def spread_market_rumor(
        self, source_actor_id: str, receiver_actor_id: str, market_id: str,
        resource_id: str, claimed_price: int, rumor_id: str,
    ) -> None:
        """Rumors affect actor beliefs only; they never change physical inventory."""
        if claimed_price <= 0:
            raise ValueError("claimed_price must be positive")
        key = self._belief_key(receiver_actor_id, market_id)
        belief = self.market_beliefs.setdefault(key, MarketBelief(receiver_actor_id, market_id, confidence=25))
        belief.believed_prices[resource_id] = claimed_price
        belief.confidence = max(5, belief.confidence - 5)
        belief.rumors.append(rumor_id)
        self.simulation._emit(
            "M5_MARKET_RUMOR_RECEIVED", actor_id=source_actor_id, target_ids=(receiver_actor_id,),
            location_id=self._market(market_id).location_id,
            payload={"rumor_id": rumor_id, "market_id": market_id, "resource_id": resource_id,
            "claimed_price": claimed_price, "physical_stock_unchanged": True},
        )
        self._sync_world_state()

    def dispatch(
        self, owner_id: str, route_id: str, resource_id: str, quantity: int, *,
        guards: int = 0, faction_id: str | None = None,
    ) -> Shipment:
        route = self._route(route_id)
        origin = self._market(route.origin_market_id)
        if quantity <= 0 or guards < 0:
            raise ActionValidationError("quantity must be positive and guards nonnegative")
        if origin.inventory_quantity(resource_id) < quantity:
            raise ActionValidationError("origin market lacks cargo")
        unit_price = origin.price_for(resource_id)
        total = unit_price * quantity
        if faction_id:
            faction = self._faction(faction_id)
            if faction.treasury < total:
                raise ActionValidationError("faction treasury cannot fund procurement")
            faction.treasury -= total
        else:
            owner = self.simulation._character(owner_id)
            if owner.currency < total:
                raise ActionValidationError("carrier cannot afford cargo")
            owner.currency -= total
        caravan_id = self.world.entity_ids.next("caravan")
        shipment_id = self.world.entity_ids.next("shipment")
        cargo = self.simulation._take_from_collection(
            origin.inventory, resource_id, quantity, owner_id=caravan_id, location_id=origin.location_id,
        )
        for lot in cargo:
            lot.owner_id = caravan_id
        risk = route.risk_score(guards)
        now = self.world.clock.elapsed_seconds
        shipment = Shipment(
            shipment_id, caravan_id, faction_id or owner_id, route.origin_market_id,
            route.destination_market_id, route_id, now, now + route.travel_hours * 3_600,
            cargo, guards, risk, recipient_faction_id=faction_id,
        )
        caravan = Caravan(caravan_id, faction_id or owner_id, route_id, shipment_id, guards)
        self.shipments[shipment_id] = shipment
        self.caravans[caravan_id] = caravan
        if faction_id:
            self._record_trade(route.origin_market_id, faction_id, "PROCUREMENT", resource_id, quantity, total)
            self._faction(faction_id).procurement_orders.append({
                "shipment_id": shipment_id, "resource_id": resource_id, "quantity": quantity,
                "origin_market_id": route.origin_market_id, "status": "IN_TRANSIT",
            })
        else:
            self._record_trade(route.origin_market_id, owner_id, "EXPORT", resource_id, quantity, total)
        self._update_market(route.origin_market_id, resource_id)
        self.simulation._emit(
            "M5_SHIPMENT_DEPARTED", actor_id=shipment.owner_id, target_ids=(shipment_id, caravan_id),
            location_id=origin.location_id,
            payload={"route_id": route_id, "origin": route.origin_market_id,
            "destination": route.destination_market_id, "resource_id": resource_id,
            "quantity": quantity, "risk": risk, "eta": shipment.arrival_at,
            "cargo_lot_ids": [lot.lot_id for lot in cargo]},
        )
        self._sync_world_state()
        return shipment

    def procure_for_faction(
        self, faction_id: str, resource_id: str, quantity: int, *, route_id: str | None = None, guards: int = 1
    ) -> Shipment:
        faction = self._faction(faction_id)
        candidates = [route for route in self.routes.values() if self._market(route.origin_market_id).inventory_quantity(resource_id) >= quantity]
        if route_id:
            candidates = [route for route in candidates if route.route_id == route_id]
        if not candidates:
            raise ActionValidationError("no route has enough stock for procurement")
        route = min(candidates, key=lambda item: (item.risk_score(guards), item.travel_hours, item.route_id))
        shipment = self.dispatch(faction_id, route.route_id, resource_id, quantity, guards=guards, faction_id=faction_id)
        self.simulation._emit(
            "M5_FACTION_PROCUREMENT_ORDERED", actor_id=faction_id, target_ids=(shipment.shipment_id,),
            location_id=self._market(route.origin_market_id).location_id,
            payload={"resource_id": resource_id, "quantity": quantity, "treasury_after": faction.treasury},
        )
        self._sync_world_state()
        return shipment

    def refresh_shortages(self, *, force: bool = False) -> list[ShortageState]:
        changed: list[ShortageState] = []
        for market_id in self.MARKET_IDS:
            market = self._market(market_id)
            for resource_id, wanted in sorted(self.demand.get(market_id, {}).items()):
                stock = market.inventory_quantity(resource_id)
                key = f"{market_id}:{resource_id}"
                if stock < wanted:
                    severity = min(100, max(1, (wanted - stock) * 100 // max(1, wanted)))
                    shortage = self.shortages.get(key)
                    if shortage is None or not shortage.active:
                        shortage = ShortageState(resource_id, market_id, wanted, stock, severity, self.world.clock.elapsed_seconds)
                        self.shortages[key] = shortage
                        self.simulation._emit(
                            "M5_SHORTAGE_DECLARED", actor_id=None, location_id=market.location_id,
                            payload={"market_id": market_id, "resource_id": resource_id,
                            "demand": wanted, "stock": stock, "severity": severity},
                        )
                        changed.append(shortage)
                    else:
                        shortage.stock = stock
                        shortage.severity = severity
                    self._update_market(market_id, resource_id)
                    self._apply_shortage_to_goals(market_id, resource_id, severity)
                elif key in self.shortages and self.shortages[key].active:
                    self.shortages[key].active = False
                    self.simulation._emit(
                        "M5_SHORTAGE_RESOLVED", actor_id=None, location_id=market.location_id,
                        payload={"market_id": market_id, "resource_id": resource_id, "stock": stock},
                    )
            if force:
                self._update_all_markets()
        return changed

    def advance_time(self, seconds: int, *, run_npcs: bool = True) -> None:
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        before = self.world.clock.elapsed_seconds
        self.simulation.advance_time(seconds, run_npcs=run_npcs)
        elapsed = self.world.clock.elapsed_seconds - before
        for node_id, condition in sorted(self.nodes.items()):
            node = self._node(node_id)
            if node_id == self.simulation.RESOURCE_NODE_ID:
                continue  # M1 already advanced this shared node.
            base_gain = elapsed * node.regeneration_per_hour * condition.health * condition.environmental_modifier // (3_600 * 10_000)
            if base_gain:
                node.current_stock = min(node.carrying_capacity, node.current_stock + base_gain)
                self.simulation._emit(
                    "M5_RESOURCE_REGENERATED", actor_id=None, location_id=node.location_id,
                    target_ids=(node_id,), payload={"quantity": base_gain, "stock_after": node.current_stock,
                    "health": condition.health},
                )
        self.resolve_due_shipments()
        self.refresh_shortages()
        self._age_market_beliefs()
        self._sync_world_state()

    def resolve_due_shipments(self) -> list[Shipment]:
        resolved: list[Shipment] = []
        for shipment in sorted(self.shipments.values(), key=lambda item: (item.arrival_at, item.shipment_id)):
            if shipment.status is not ShipmentStatus.IN_TRANSIT or shipment.arrival_at > self.world.clock.elapsed_seconds:
                continue
            route = self._route(shipment.route_id)
            route_risk = min(95, max(0, shipment.risk_at_departure + route.recent_combat * 2 + route.shortage_pressure // 2))
            roll = self.world.rng.randint(1, 100)
            if roll <= route_risk:
                shipment.status = ShipmentStatus.LOST
                for lot in shipment.cargo:
                    lot.quantity = 0
                self.caravans[shipment.caravan_id].status = ShipmentStatus.LOST
                self._simulation_market_event("M5_SHIPMENT_LOST", shipment, {"risk": route_risk, "roll": roll})
            else:
                destination = self._market(shipment.destination_market_id)
                for lot in shipment.cargo:
                    lot.owner_id = shipment.recipient_faction_id or destination.market_id
                    lot.location_id = destination.location_id
                    if shipment.recipient_faction_id:
                        faction = self._faction(shipment.recipient_faction_id)
                        faction.warehouse[lot.lot_id] = lot
                        faction.reserves[lot.definition_id] = faction.reserves.get(lot.definition_id, 0) + lot.quantity
                    else:
                        destination.inventory[lot.lot_id] = lot
                    resource_id = lot.definition_id
                shipment.status = ShipmentStatus.ARRIVED
                self.caravans[shipment.caravan_id].status = ShipmentStatus.ARRIVED
                self._simulation_market_event("M5_SHIPMENT_ARRIVED", shipment, {"risk": route_risk, "roll": roll})
                self._update_market(destination.market_id, resource_id)
            shipment.resolved_at = self.world.clock.elapsed_seconds
            resolved.append(shipment)
            for faction in self.factions.values():
                for order in faction.procurement_orders:
                    if order.get("shipment_id") == shipment.shipment_id:
                        order["status"] = shipment.status.value
        if resolved:
            self.refresh_shortages()
            self._sync_world_state()
        return resolved

    def add_route_pressure(
        self, route_id: str, *, combat: int = 0, criminal: int = 0, shortage: int = 0, patrol: int = 0
    ) -> None:
        route = self._route(route_id)
        route.recent_combat = max(0, min(20, route.recent_combat + combat))
        route.criminal_activity = max(0, min(20, route.criminal_activity + criminal))
        route.shortage_pressure = max(0, min(50, route.shortage_pressure + shortage))
        route.patrol_strength = max(0, min(100, route.patrol_strength + patrol))
        self.simulation._emit(
            "M5_ROUTE_RISK_CHANGED", actor_id=None,
            location_id=self._market(route.origin_market_id).location_id,
            target_ids=(route_id,), payload={"risk": route.risk_score(), "combat": route.recent_combat,
            "criminal_activity": route.criminal_activity, "shortage_pressure": route.shortage_pressure,
            "patrol_strength": route.patrol_strength},
        )
        self._sync_world_state()

    def market_summary(self) -> dict[str, Any]:
        return {
            market_id: {
                "location_id": self._market(market_id).location_id,
                "currency": self._market(market_id).currency,
                "stock": {resource_id: self._market(market_id).inventory_quantity(resource_id)
                          for resource_id in self.resource_groups["food"]},
                "prices": {resource_id: self._market(market_id).price_for(resource_id)
                           for resource_id in self.resource_groups["food"]},
                "active_shortages": sorted(resource_id for resource_id in self.demand[market_id]
                                            if self.shortages.get(f"{market_id}:{resource_id}", ShortageState(resource_id, market_id, 0, 0, 0, 0, False)).active),
            }
            for market_id in self.MARKET_IDS
        }

    def summary(self) -> dict[str, Any]:
        return {
            "resource_definitions": len(self.simulation.resource_definitions),
            "resource_nodes": len(self.nodes),
            "markets": len(self.MARKET_IDS),
            "routes": len(self.routes),
            "active_shortages": sum(item.active for item in self.shortages.values()),
            "shipments": {status.value: sum(item.status is status for item in self.shipments.values()) for status in ShipmentStatus},
            "market_summary": self.market_summary(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "resource_groups": self.resource_groups,
            "nodes": {key: value.to_dict() for key, value in sorted(self.nodes.items())},
            "routes": {key: value.to_dict() for key, value in sorted(self.routes.items())},
            "shipments": {key: value.to_dict() for key, value in sorted(self.shipments.items())},
            "caravans": {key: value.to_dict() for key, value in sorted(self.caravans.items())},
            "factions": {key: value.to_dict() for key, value in sorted(self.factions.items())},
            "market_beliefs": {key: value.to_dict() for key, value in sorted(self.market_beliefs.items())},
            "demand": self.demand,
            "shortages": {key: value.to_dict() for key, value in sorted(self.shortages.items())},
            "npc_goals": self.npc_goals,
            "trade_history": self.trade_history,
        }

    def _load_dict(self, data: dict[str, Any]) -> None:
        if int(data.get("schema_version", 0)) > self.SCHEMA_VERSION:
            raise ValueError("M5 save is newer than this engine")
        self.resource_groups = {str(key): list(value) for key, value in data.get("resource_groups", {}).items()}
        self.nodes = {key: ResourceNodeCondition.from_dict(value) for key, value in data.get("nodes", {}).items()}
        self.routes = {key: RouteDefinition.from_dict(value) for key, value in data.get("routes", {}).items()}
        self.shipments = {key: Shipment.from_dict(value) for key, value in data.get("shipments", {}).items()}
        self.caravans = {key: Caravan.from_dict(value) for key, value in data.get("caravans", {}).items()}
        self.factions = {key: FactionEconomy.from_dict(value) for key, value in data.get("factions", {}).items()}
        self.market_beliefs = {key: MarketBelief.from_dict(value) for key, value in data.get("market_beliefs", {}).items()}
        self.demand = {str(key): {str(k): int(v) for k, v in value.items()} for key, value in data.get("demand", {}).items()}
        self.shortages = {key: ShortageState.from_dict(value) for key, value in data.get("shortages", {}).items()}
        self.npc_goals = {str(key): str(value) for key, value in data.get("npc_goals", {}).items()}
        self.trade_history = list(data.get("trade_history", []))

    def _sync_world_state(self) -> None:
        self.simulation._sync_world_state()
        self.world.game_state["m5_economy"] = self.to_dict()

    def _update_all_markets(self, *, emit: bool = True) -> None:
        for market_id, demands in sorted(self.demand.items()):
            for resource_id in sorted(demands):
                self._update_market(market_id, resource_id, emit=emit)

    def _update_market(self, market_id: str, resource_id: str, *, emit: bool = True) -> None:
        market = self._market(market_id)
        base = market.base_prices.get(resource_id, self.simulation.resource_definitions[resource_id].base_reference_value)
        stock = market.inventory_quantity(resource_id)
        wanted = self.demand.get(market_id, {}).get(resource_id, 0)
        # Local supply/demand pressure changes only this market's quote.
        adjustment = 0 if wanted <= 0 else max(-market.max_price_shift, min(market.max_price_shift, (wanted - stock) * 2 // max(1, wanted)))
        old_price = market.price_for(resource_id)
        market.price_adjustments[resource_id] = adjustment
        new_price = market.price_for(resource_id)
        if emit and old_price != new_price:
            self.simulation._emit(
                "M5_MARKET_PRICE_CHANGED", actor_id=None, location_id=market.location_id,
                target_ids=(market_id,), payload={"resource_id": resource_id, "old_price": old_price,
                "new_price": new_price, "stock": stock, "demand": wanted,
                "provenance": market.price_provenance},
            )

    def _apply_shortage_to_goals(self, market_id: str, resource_id: str, severity: int) -> None:
        food_ids = set(self.resource_groups["food"]) | {self.simulation.FOOD_RESOURCE_ID}
        if resource_id in food_ids:
            for index, npc_id in enumerate(sorted(self.simulation.npc_ids)):
                self.npc_goals[npc_id] = "SECURE_GU_FOOD" if severity >= 40 or index % 2 == 0 else "SEEK_SUBSTITUTE"
        for faction in self.factions.values():
            if resource_id in food_ids:
                faction.shortage_intensity[resource_id] = severity
        for route in self.routes.values():
            if route.origin_market_id == market_id or route.destination_market_id == market_id:
                route.shortage_pressure = min(50, max(route.shortage_pressure, severity // 4))

    def _record_trade(self, market_id: str, actor_id: str, action: str, resource_id: str, quantity: int, total: int) -> None:
        self.trade_history.append({
            "timestamp": self.world.clock.elapsed_seconds, "market_id": market_id,
            "actor_id": actor_id, "action": action, "resource_id": resource_id,
            "quantity": quantity, "total": total,
        })

    def _emit_trade(self, event_type: str, market: LocalMarket, actor_id: str, resource_id: str, quantity: int, total: int) -> None:
        self.simulation._emit(
            event_type, actor_id=actor_id, location_id=market.location_id, target_ids=(market.market_id,),
            payload={"resource_id": resource_id, "quantity": quantity, "total": total,
            "unit_price": total // quantity, "stock_after": market.inventory_quantity(resource_id)},
        )

    def _simulation_market_event(self, event_type: str, shipment: Shipment, extra: dict[str, Any]) -> None:
        self.simulation._emit(
            event_type, actor_id=shipment.owner_id,
            target_ids=(shipment.shipment_id, shipment.caravan_id),
            location_id=self._market(shipment.destination_market_id).location_id,
            payload={"origin": shipment.origin_market_id, "destination": shipment.destination_market_id,
            "route_id": shipment.route_id, "cargo_lots": [lot.to_dict() for lot in shipment.cargo], **extra},
        )

    def _age_market_beliefs(self) -> None:
        now = self.world.clock.elapsed_seconds
        for belief in self.market_beliefs.values():
            hours = max(0, now - belief.last_observed_at) // 3_600
            if hours:
                belief.confidence = max(5, belief.confidence - int(hours))
                belief.last_observed_at = now

    @staticmethod
    def _belief_key(actor_id: str, market_id: str) -> str:
        return f"{actor_id}:{market_id}"

    def _node(self, node_id: str) -> ResourceNode:
        try:
            return self.simulation.resource_nodes[node_id]
        except KeyError as exc:
            raise ActionValidationError(f"unknown resource node: {node_id}") from exc

    def _market(self, market_id: str) -> LocalMarket:
        try:
            return self.simulation.markets[market_id]
        except KeyError as exc:
            raise ActionValidationError(f"unknown market: {market_id}") from exc

    def _route(self, route_id: str) -> RouteDefinition:
        try:
            return self.routes[route_id]
        except KeyError as exc:
            raise ActionValidationError(f"unknown route: {route_id}") from exc

    def _faction(self, faction_id: str) -> FactionEconomy:
        try:
            return self.factions[faction_id]
        except KeyError as exc:
            raise ActionValidationError(f"unknown faction economy: {faction_id}") from exc
