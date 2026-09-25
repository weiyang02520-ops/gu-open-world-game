"""Deterministic Day 1~2 simulation and action pipeline."""

from __future__ import annotations

from typing import Any, Iterable

from ..core.events import DomainEvent
from ..core.state import WorldState
from ..provenance import Provenance
from ..save import load_world, save_world
from .balance import GAME_EXTENSION_BALANCE as B
from .models import (
    ActionIntent,
    ActionResult,
    ActionType,
    Character,
    Controller,
    CultivationState,
    GuDefinition,
    GuInstance,
    HungerState,
    LocalMarket,
    ResourceDefinition,
    ResourceLot,
    ResourceNode,
)


class ActionValidationError(ValueError):
    """Raised when an ActionIntent cannot be applied to the current state."""


class Simulation:
    """Headless M1 world with one authoritative WorldState event log."""

    M1_SCHEMA_VERSION = 1
    LOCATION_ID = "location-southern-grove"
    MARKET_ID = "market-southern-grove"
    RESOURCE_NODE_ID = "resource-node-spirit-grove"
    FOOD_RESOURCE_ID = "resource-spirit-grass"

    def __init__(self, world: WorldState) -> None:
        self.world = world
        self.event_bus = world.create_event_bus()
        self.characters: dict[str, Character] = {}
        self.gu_definitions: dict[str, GuDefinition] = {}
        self.gu_instances: dict[str, GuInstance] = {}
        self.resource_definitions: dict[str, ResourceDefinition] = {}
        self.resource_nodes: dict[str, ResourceNode] = {}
        self.markets: dict[str, LocalMarket] = {}
        self.player_id: str = ""
        self.npc_ids: list[str] = []
        self._processing_npcs = False

    @classmethod
    def new(cls, seed: int) -> "Simulation":
        simulation = cls(WorldState.new(seed))
        simulation._bootstrap()
        simulation._sync_world_state()
        return simulation

    @classmethod
    def from_world_state(cls, world: WorldState) -> "Simulation":
        if not world.game_state:
            raise ValueError("world state does not contain M1 game_state")
        data = world.game_state
        if int(data.get("m1_schema_version", 0)) > cls.M1_SCHEMA_VERSION:
            raise ValueError("M1 game_state is newer than this simulator")

        simulation = cls(world)
        simulation.player_id = str(data["player_id"])
        simulation.npc_ids = [str(item) for item in data.get("npc_ids", [])]
        simulation.characters = {
            key: Character.from_dict(value)
            for key, value in data.get("characters", {}).items()
        }
        simulation.gu_definitions = {
            key: GuDefinition.from_dict(value)
            for key, value in data.get("gu_definitions", {}).items()
        }
        simulation.gu_instances = {
            key: GuInstance.from_dict(value)
            for key, value in data.get("gu_instances", {}).items()
        }
        simulation.resource_definitions = {
            key: ResourceDefinition.from_dict(value)
            for key, value in data.get("resource_definitions", {}).items()
        }
        simulation.resource_nodes = {
            key: ResourceNode.from_dict(value)
            for key, value in data.get("resource_nodes", {}).items()
        }
        simulation.markets = {
            key: LocalMarket.from_dict(value)
            for key, value in data.get("markets", {}).items()
        }
        return simulation

    def _bootstrap(self) -> None:
        self.resource_definitions[self.FOOD_RESOURCE_ID] = ResourceDefinition(
            definition_id=self.FOOD_RESOURCE_ID,
            name="Spirit Grass",
            unit="blade",
            base_reference_value=B["market_food_base_price"],
        )
        self.resource_nodes[self.RESOURCE_NODE_ID] = ResourceNode(
            node_id=self.RESOURCE_NODE_ID,
            location_id=self.LOCATION_ID,
            resource_definition_id=self.FOOD_RESOURCE_ID,
            current_stock=B["resource_initial_stock"],
            carrying_capacity=B["resource_capacity"],
            regeneration_per_hour=B["resource_regeneration_per_hour"],
        )
        self.markets[self.MARKET_ID] = LocalMarket(
            market_id=self.MARKET_ID,
            location_id=self.LOCATION_ID,
            currency=B["market_starting_currency"],
            base_prices={self.FOOD_RESOURCE_ID: B["market_food_base_price"]},
        )

        for definition_id, name in (
            ("gu-moonlit-moth", "Moonlit Moth"),
            ("gu-stone-skin-beetle", "Stone Skin Beetle"),
            ("gu-clear-stream-worm", "Clear Stream Worm"),
        ):
            self.gu_definitions[definition_id] = GuDefinition(
                definition_id=definition_id,
                name=name,
                rank=B["default_rank"],
                food_definition_id=self.FOOD_RESOURCE_ID,
            )

        market = self.markets[self.MARKET_ID]
        market_lot = ResourceLot(
            lot_id=self.world.entity_ids.next("lot"),
            definition_id=self.FOOD_RESOURCE_ID,
            quantity=B["market_starting_food_lots"],
            quality=B["default_resource_quality"],
            owner_id=self.MARKET_ID,
            location_id=self.LOCATION_ID,
            freshness_hours=0,
        )
        market.inventory[market_lot.lot_id] = market_lot

        self.player_id = self.world.entity_ids.next("character")
        player = Character(
            character_id=self.player_id,
            name="自创蛊师",
            controller=Controller.HUMAN,
            location_id=self.LOCATION_ID,
            currency=B["player_starting_currency"],
            cultivation=CultivationState(
                aptitude=68,
                aperture_capacity=110,
                primeval_current=70,
                primeval_maximum=110,
            ),
        )
        self.characters[player.character_id] = player
        for definition_id in self.gu_definitions:
            self._add_gu(player.character_id, definition_id)

        npc_names = ("沈砾", "林七", "顾禾")
        for index in range(B["npc_count"]):
            npc_id = self.world.entity_ids.next("character")
            npc = Character(
                character_id=npc_id,
                name=npc_names[index],
                controller=Controller.AI,
                location_id=self.LOCATION_ID,
                currency=B["npc_starting_currency"],
                cultivation=CultivationState(
                    aptitude=55 + index * 3,
                    aperture_capacity=100,
                    primeval_current=55,
                    primeval_maximum=100,
                ),
            )
            self.characters[npc_id] = npc
            self.npc_ids.append(npc_id)
            definition_id = list(self.gu_definitions)[index % len(self.gu_definitions)]
            self._add_gu(npc_id, definition_id, satiety=64)

    def _add_gu(self, owner_id: str, definition_id: str, satiety: int | None = None) -> str:
        definition = self.gu_definitions[definition_id]
        instance_id = self.world.entity_ids.next("gu")
        instance = GuInstance(
            instance_id=instance_id,
            definition_id=definition_id,
            owner_id=owner_id,
            rank=definition.rank,
            satiety=satiety if satiety is not None else B["gu_starting_satiety"],
            hunger_state=GuInstance.derive_hunger_state(
                satiety if satiety is not None else B["gu_starting_satiety"],
                definition.satiety_maximum,
            ),
        )
        self.gu_instances[instance_id] = instance
        self.characters[owner_id].owned_gu_ids.append(instance_id)
        return instance_id

    def execute(self, intent: ActionIntent) -> ActionResult:
        """Validate and apply one action through the M1 action pipeline."""

        actor = self._character(intent.actor_id)
        event_ids = self._perform_action(intent, consume_time=True)
        actor.action_count += 1
        self._sync_world_state()
        return ActionResult(
            success=True,
            action_type=intent.action_type,
            actor_id=actor.character_id,
            message=f"{intent.action_type.value} applied",
            event_ids=tuple(event_ids),
            elapsed_seconds=self.world.clock.elapsed_seconds,
        )

    def advance_time(self, seconds: int, *, run_npcs: bool = True) -> None:
        self._advance_time_internal(seconds, run_npcs=run_npcs)
        self._sync_world_state()

    def save(self, path: str) -> None:
        self._sync_world_state()
        save_world(self.world, path)

    @classmethod
    def load(cls, path: str) -> "Simulation":
        return cls.from_world_state(load_world(path))

    def summary(self) -> dict[str, Any]:
        player = self.characters[self.player_id]
        node = self.resource_nodes[self.RESOURCE_NODE_ID]
        market = self.markets[self.MARKET_ID]
        event_counts: dict[str, int] = {}
        for event in self.world.event_log:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        return {
            "day": self.world.clock.day_number,
            "elapsed_hours": self.world.clock.elapsed_seconds // 3_600,
            "player": {
                "id": player.character_id,
                "currency": player.currency,
                "inventory": player.inventory_quantity(self.FOOD_RESOURCE_ID),
                "gu_count": len(player.owned_gu_ids),
                "primeval_current": player.cultivation.primeval_current,
                "wall_progress": player.cultivation.wall_progress,
            },
            "resource_node": {
                "stock": node.current_stock,
                "capacity": node.carrying_capacity,
            },
            "market": {
                "currency": market.currency,
                "food_stock": market.inventory_quantity(self.FOOD_RESOURCE_ID),
                "food_price": market.price_for(self.FOOD_RESOURCE_ID),
            },
            "npcs": [
                {
                    "id": npc_id,
                    "actions": self.characters[npc_id].action_count,
                    "currency": self.characters[npc_id].currency,
                    "food": self.characters[npc_id].inventory_quantity(self.FOOD_RESOURCE_ID),
                }
                for npc_id in self.npc_ids
            ],
            "event_count": len(self.world.event_log),
            "event_types": event_counts,
        }

    def event_log_tail(self, count: int = 12) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.world.event_log[-count:]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "m1_schema_version": self.M1_SCHEMA_VERSION,
            "location_id": self.LOCATION_ID,
            "market_id": self.MARKET_ID,
            "resource_node_id": self.RESOURCE_NODE_ID,
            "food_resource_id": self.FOOD_RESOURCE_ID,
            "player_id": self.player_id,
            "npc_ids": list(self.npc_ids),
            "characters": {
                key: value.to_dict() for key, value in sorted(self.characters.items())
            },
            "gu_definitions": {
                key: value.to_dict() for key, value in sorted(self.gu_definitions.items())
            },
            "gu_instances": {
                key: value.to_dict() for key, value in sorted(self.gu_instances.items())
            },
            "resource_definitions": {
                key: value.to_dict() for key, value in sorted(self.resource_definitions.items())
            },
            "resource_nodes": {
                key: value.to_dict() for key, value in sorted(self.resource_nodes.items())
            },
            "markets": {key: value.to_dict() for key, value in sorted(self.markets.items())},
        }

    def _sync_world_state(self) -> None:
        self.world.game_state = self.to_dict()

    def _perform_action(self, intent: ActionIntent, *, consume_time: bool) -> list[str]:
        if intent.action_type is ActionType.GATHER:
            event_ids = self._perform_gather(intent)
            duration = B["gather_duration_seconds"]
        elif intent.action_type is ActionType.BUY:
            event_ids = self._perform_buy(intent)
            duration = B["market_trade_duration_seconds"]
        elif intent.action_type is ActionType.SELL:
            event_ids = self._perform_sell(intent)
            duration = B["market_trade_duration_seconds"]
        elif intent.action_type is ActionType.FEED_GU:
            event_ids = self._perform_feed(intent)
            duration = B["feed_duration_seconds"]
        elif intent.action_type is ActionType.CULTIVATE:
            event_ids = self._perform_cultivate(intent)
            duration = B["cultivate_duration_seconds"]
        elif intent.action_type is ActionType.WAIT:
            duration = self._validate_duration(intent.duration_seconds)
            event_ids = []
        else:  # pragma: no cover - StrEnum exhaustiveness guard
            raise ActionValidationError(f"unsupported action: {intent.action_type}")

        if consume_time and duration:
            self._advance_time_internal(duration, run_npcs=True)
        return event_ids

    def _perform_gather(self, intent: ActionIntent) -> list[str]:
        actor = self._character(intent.actor_id)
        resource_id = intent.resource_id or self.FOOD_RESOURCE_ID
        quantity = self._validate_quantity(intent.quantity)
        node = self.resource_nodes[self.RESOURCE_NODE_ID]
        if resource_id != node.resource_definition_id:
            raise ActionValidationError("this M1 node only produces its configured resource")
        if node.current_stock < quantity:
            raise ActionValidationError("resource node does not have enough stock")

        node.current_stock -= quantity
        node.extraction_pressure += quantity
        lot = ResourceLot(
            lot_id=self.world.entity_ids.next("lot"),
            definition_id=resource_id,
            quantity=quantity,
            quality=B["default_resource_quality"],
            owner_id=actor.character_id,
            location_id=actor.location_id,
            source_node_id=node.node_id,
        )
        actor.add_lot(lot)
        return [
            self._emit(
                "RESOURCE_GATHERED",
                actor_id=actor.character_id,
                location_id=node.location_id,
                payload={
                    "resource_id": resource_id,
                    "quantity": quantity,
                    "node_id": node.node_id,
                    "node_stock_after": node.current_stock,
                    "balance_provenance": Provenance.GAME_EXTENSION.value,
                },
            )
        ]

    def _perform_buy(self, intent: ActionIntent) -> list[str]:
        actor = self._character(intent.actor_id)
        resource_id = intent.resource_id or self.FOOD_RESOURCE_ID
        quantity = self._validate_quantity(intent.quantity)
        market = self.markets[self.MARKET_ID]
        available = market.inventory_quantity(resource_id)
        if available < quantity:
            raise ActionValidationError("market does not have enough inventory")
        unit_price = market.price_for(resource_id)
        total_price = unit_price * quantity
        if actor.currency < total_price:
            raise ActionValidationError("actor cannot afford this purchase")
        if market.currency < 0:  # defensive invariant
            raise ActionValidationError("market currency invariant is broken")

        moved = self._take_from_collection(
            market.inventory,
            resource_id,
            quantity,
            owner_id=actor.character_id,
            location_id=actor.location_id,
        )
        for lot in moved:
            actor.add_lot(lot)
        actor.currency -= total_price
        market.currency += total_price
        market.apply_buy_pressure(resource_id)
        return [
            self._emit(
                "MARKET_BUY",
                actor_id=actor.character_id,
                location_id=market.location_id,
                payload={
                    "market_id": market.market_id,
                    "resource_id": resource_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "market_stock_after": market.inventory_quantity(resource_id),
                    "balance_provenance": market.price_provenance,
                },
            )
        ]

    def _perform_sell(self, intent: ActionIntent) -> list[str]:
        actor = self._character(intent.actor_id)
        resource_id = intent.resource_id or self.FOOD_RESOURCE_ID
        quantity = self._validate_quantity(intent.quantity)
        market = self.markets[self.MARKET_ID]
        if actor.inventory_quantity(resource_id) < quantity:
            raise ActionValidationError("actor does not own enough resource to sell")
        unit_price = market.price_for(resource_id)
        total_price = unit_price * quantity
        if market.currency < total_price:
            raise ActionValidationError("market treasury cannot afford this sale")

        moved = self._take_from_collection(
            actor.inventory,
            resource_id,
            quantity,
            owner_id=market.market_id,
            location_id=market.location_id,
        )
        for lot in moved:
            market.inventory[lot.lot_id] = lot
        actor.currency += total_price
        market.currency -= total_price
        market.apply_sell_pressure(resource_id)
        return [
            self._emit(
                "MARKET_SELL",
                actor_id=actor.character_id,
                location_id=market.location_id,
                payload={
                    "market_id": market.market_id,
                    "resource_id": resource_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "market_stock_after": market.inventory_quantity(resource_id),
                    "balance_provenance": market.price_provenance,
                },
            )
        ]

    def _perform_feed(self, intent: ActionIntent) -> list[str]:
        actor = self._character(intent.actor_id)
        if not intent.gu_id:
            raise ActionValidationError("FEED_GU requires gu_id")
        gu = self.gu_instances.get(intent.gu_id)
        if gu is None or gu.owner_id != actor.character_id:
            raise ActionValidationError("actor does not own this Gu")
        definition = self.gu_definitions[gu.definition_id]
        food_id = definition.food_definition_id
        quantity = definition.feed_quantity
        if actor.inventory_quantity(food_id) < quantity:
            raise ActionValidationError("actor does not own enough Gu food")

        self._consume_from_collection(actor.inventory, food_id, quantity)
        old_satiety = gu.satiety
        old_state = gu.hunger_state
        gu.satiety = min(definition.satiety_maximum, gu.satiety + B["gu_feed_satiety_gain"])
        gu.hunger_state = GuInstance.derive_hunger_state(gu.satiety, definition.satiety_maximum)
        event_ids = [
            self._emit(
                "GU_FED",
                actor_id=actor.character_id,
                target_ids=(gu.instance_id,),
                location_id=actor.location_id,
                payload={
                    "gu_id": gu.instance_id,
                    "food_resource_id": food_id,
                    "quantity": quantity,
                    "satiety_before": old_satiety,
                    "satiety_after": gu.satiety,
                    "balance_provenance": Provenance.GAME_EXTENSION.value,
                },
            )
        ]
        if old_satiety != gu.satiety or old_state != gu.hunger_state:
            event_ids.append(
                self._emit(
                    "GU_HUNGER_CHANGED",
                    actor_id=actor.character_id,
                    target_ids=(gu.instance_id,),
                    location_id=actor.location_id,
                    payload={
                        "gu_id": gu.instance_id,
                        "satiety_before": old_satiety,
                        "satiety_after": gu.satiety,
                        "state_before": old_state.value,
                        "state_after": gu.hunger_state.value,
                        "reason": "fed",
                    },
                )
            )
        return event_ids

    def _perform_cultivate(self, intent: ActionIntent) -> list[str]:
        actor = self._character(intent.actor_id)
        cultivation = actor.cultivation
        cost = B["cultivate_essence_cost"]
        if cultivation.primeval_current < cost:
            raise ActionValidationError("not enough primeval essence")
        before_essence = cultivation.primeval_current
        before_wall = cultivation.wall_progress
        cultivation.primeval_current -= cost
        cultivation.wall_progress = min(
            cultivation.wall_threshold,
            cultivation.wall_progress + B["cultivate_wall_progress"],
        )
        return [
            self._emit(
                "CULTIVATION_PROGRESS",
                actor_id=actor.character_id,
                location_id=actor.location_id,
                payload={
                    "essence_before": before_essence,
                    "essence_after": cultivation.primeval_current,
                    "wall_progress_before": before_wall,
                    "wall_progress_after": cultivation.wall_progress,
                    "essence_cost": cost,
                    "balance_provenance": Provenance.GAME_EXTENSION.value,
                },
            )
        ]

    def _advance_time_internal(self, seconds: int, *, run_npcs: bool) -> None:
        if not isinstance(seconds, int) or isinstance(seconds, bool):
            raise TypeError("seconds must be an integer")
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        if seconds == 0:
            return

        remaining = seconds
        while remaining:
            step = min(3_600, remaining)
            self.world.clock.advance(step)
            self._update_gu_hunger(step)
            self._regenerate_resources(step)
            if run_npcs and not self._processing_npcs:
                self._run_npc_round()
            remaining -= step
        self._emit(
            "TIME_ADVANCED",
            actor_id=None,
            location_id=self.LOCATION_ID,
            payload={"seconds": seconds, "elapsed_seconds": self.world.clock.elapsed_seconds},
        )

    def _update_gu_hunger(self, seconds: int) -> None:
        for gu_id in sorted(self.gu_instances):
            gu = self.gu_instances[gu_id]
            definition = self.gu_definitions[gu.definition_id]
            old_satiety, old_state = gu.update_hunger(seconds, definition)
            if old_satiety != gu.satiety or old_state != gu.hunger_state:
                self._emit(
                    "GU_HUNGER_CHANGED",
                    actor_id=gu.owner_id,
                    target_ids=(gu.instance_id,),
                    location_id=self.LOCATION_ID,
                    payload={
                        "gu_id": gu.instance_id,
                        "satiety_before": old_satiety,
                        "satiety_after": gu.satiety,
                        "state_before": old_state.value,
                        "state_after": gu.hunger_state.value,
                        "reason": "time",
                    },
                )

    def _regenerate_resources(self, seconds: int) -> None:
        node = self.resource_nodes[self.RESOURCE_NODE_ID]
        gained = node.regenerate(seconds)
        if gained:
            self._emit(
                "RESOURCE_REGENERATED",
                actor_id=None,
                location_id=node.location_id,
                payload={
                    "node_id": node.node_id,
                    "resource_id": node.resource_definition_id,
                    "quantity": gained,
                    "stock_after": node.current_stock,
                    "balance_provenance": node.provenance,
                },
            )

    def _run_npc_round(self) -> None:
        self._processing_npcs = True
        try:
            for npc_id in sorted(self.npc_ids):
                intent, reason = self._choose_npc_action(npc_id)
                npc = self.characters[npc_id]
                self._emit(
                    "NPC_ACTION_SELECTED",
                    actor_id=npc_id,
                    location_id=npc.location_id,
                    payload={
                        "action_type": intent.action_type.value,
                        "reason": reason,
                        "resource_id": intent.resource_id,
                        "gu_id": intent.gu_id,
                    },
                )
                if intent.action_type is not ActionType.WAIT:
                    self._perform_action(intent, consume_time=False)
                npc.action_count += 1
        finally:
            self._processing_npcs = False

    def _choose_npc_action(self, npc_id: str) -> tuple[ActionIntent, str]:
        npc = self.characters[npc_id]
        food_id = self.FOOD_RESOURCE_ID
        hungry_gu = next(
            (
                self.gu_instances[gu_id]
                for gu_id in sorted(npc.owned_gu_ids)
                if self.gu_instances[gu_id].hunger_state
                in {HungerState.HUNGRY, HungerState.STARVING, HungerState.CRITICAL}
            ),
            None,
        )
        if hungry_gu and npc.inventory_quantity(food_id) >= self.gu_definitions[hungry_gu.definition_id].feed_quantity:
            return (
                ActionIntent(ActionType.FEED_GU, npc_id, gu_id=hungry_gu.instance_id),
                "gu_feeding_need",
            )

        market = self.markets[self.MARKET_ID]
        unit_price = market.price_for(food_id)
        if hungry_gu and market.inventory_quantity(food_id) and npc.currency >= unit_price:
            return (
                ActionIntent(ActionType.BUY, npc_id, resource_id=food_id, quantity=1),
                "gu_feeding_need",
            )
        if npc.inventory_quantity(food_id) >= 3 and market.currency >= unit_price:
            return (
                ActionIntent(ActionType.SELL, npc_id, resource_id=food_id, quantity=1),
                "market_liquidity_need",
            )
        node = self.resource_nodes[self.RESOURCE_NODE_ID]
        if node.current_stock:
            return (
                ActionIntent(ActionType.GATHER, npc_id, resource_id=food_id, quantity=1),
                "resource_stock_need",
            )
        return ActionIntent(ActionType.WAIT, npc_id, duration_seconds=3_600), "no_available_action"

    def _take_from_collection(
        self,
        collection: dict[str, ResourceLot],
        definition_id: str,
        quantity: int,
        *,
        owner_id: str,
        location_id: str,
    ) -> list[ResourceLot]:
        remaining = quantity
        moved: list[ResourceLot] = []
        for lot_id in sorted(list(collection)):
            if remaining <= 0:
                break
            lot = collection[lot_id]
            if lot.definition_id != definition_id:
                continue
            taken = min(remaining, lot.quantity)
            remaining -= taken
            if taken == lot.quantity:
                del collection[lot_id]
                lot.owner_id = owner_id
                lot.location_id = location_id
                moved.append(lot)
            else:
                lot.quantity -= taken
                moved.append(
                    ResourceLot(
                        lot_id=self.world.entity_ids.next("lot"),
                        definition_id=lot.definition_id,
                        quantity=taken,
                        quality=lot.quality,
                        owner_id=owner_id,
                        location_id=location_id,
                        source_node_id=lot.source_node_id,
                        freshness_hours=lot.freshness_hours,
                    )
                )
        if remaining:
            raise ActionValidationError("resource transfer quantity is not available")
        return moved

    @staticmethod
    def _consume_from_collection(
        collection: dict[str, ResourceLot], definition_id: str, quantity: int
    ) -> None:
        remaining = quantity
        for lot_id in sorted(list(collection)):
            if remaining <= 0:
                break
            lot = collection[lot_id]
            if lot.definition_id != definition_id:
                continue
            consumed = min(remaining, lot.quantity)
            lot.quantity -= consumed
            remaining -= consumed
            if lot.quantity == 0:
                del collection[lot_id]
        if remaining:
            raise ActionValidationError("resource consumption quantity is not available")

    def _emit(
        self,
        event_type: str,
        *,
        actor_id: str | None,
        payload: dict[str, Any],
        target_ids: Iterable[str] = (),
        location_id: str | None = None,
    ) -> str:
        event = DomainEvent(
            event_id=self.world.entity_ids.next("event"),
            event_type=event_type,
            timestamp=self.world.clock.elapsed_seconds,
            actor_id=actor_id,
            target_ids=tuple(target_ids),
            location_id=location_id,
            payload=payload,
            source="M1_SIMULATION",
            provenance=Provenance.GAME_EXTENSION.value,
        )
        self.event_bus.publish(event)
        self.event_bus.dispatch_pending()
        return event.event_id

    def _character(self, character_id: str) -> Character:
        try:
            return self.characters[character_id]
        except KeyError as exc:
            raise ActionValidationError(f"unknown character: {character_id}") from exc

    @staticmethod
    def _validate_quantity(quantity: int) -> int:
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ActionValidationError("quantity must be a positive integer")
        return quantity

    @staticmethod
    def _validate_duration(duration: int | None) -> int:
        if duration is None:
            raise ActionValidationError("WAIT requires duration_seconds")
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            raise ActionValidationError("duration_seconds must be a positive integer")
        return duration
