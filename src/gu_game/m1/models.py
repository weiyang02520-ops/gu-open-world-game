"""Serializable domain records used by the M1 sandbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from .balance import GAME_EXTENSION_BALANCE as B


class Controller(StrEnum):
    HUMAN = "HUMAN"
    AI = "AI"


class HungerState(StrEnum):
    FULL = "FULL"
    NORMAL = "NORMAL"
    HUNGRY = "HUNGRY"
    STARVING = "STARVING"
    CRITICAL = "CRITICAL"


class ActionType(StrEnum):
    GATHER = "GATHER"
    BUY = "BUY"
    SELL = "SELL"
    FEED_GU = "FEED_GU"
    CULTIVATE = "CULTIVATE"
    WAIT = "WAIT"


@dataclass
class CultivationState:
    rank: int = B["default_rank"]
    minor_stage: str = "INITIAL"
    aptitude: int = B["default_aptitude"]
    aperture_capacity: int = B["default_aperture_capacity"]
    primeval_current: int = B["default_primeval_current"]
    primeval_maximum: int = B["default_primeval_maximum"]
    essence_quality: int = B["default_essence_quality"]
    wall_progress: int = B["default_wall_progress"]
    wall_threshold: int = B["default_wall_threshold"]

    def __post_init__(self) -> None:
        if self.aptitude < 0 or self.aperture_capacity <= 0:
            raise ValueError("cultivation capacity values are invalid")
        if not 0 <= self.primeval_current <= self.primeval_maximum:
            raise ValueError("primeval_current must be within its maximum")
        if self.wall_progress < 0 or self.wall_threshold <= 0:
            raise ValueError("wall progress values are invalid")

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "minor_stage": self.minor_stage,
            "aptitude": self.aptitude,
            "aperture_capacity": self.aperture_capacity,
            "primeval_current": self.primeval_current,
            "primeval_maximum": self.primeval_maximum,
            "essence_quality": self.essence_quality,
            "wall_progress": self.wall_progress,
            "wall_threshold": self.wall_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CultivationState":
        return cls(
            rank=int(data["rank"]),
            minor_stage=str(data["minor_stage"]),
            aptitude=int(data["aptitude"]),
            aperture_capacity=int(data["aperture_capacity"]),
            primeval_current=int(data["primeval_current"]),
            primeval_maximum=int(data["primeval_maximum"]),
            essence_quality=int(data["essence_quality"]),
            wall_progress=int(data["wall_progress"]),
            wall_threshold=int(data["wall_threshold"]),
        )


@dataclass
class ResourceDefinition:
    definition_id: str
    name: str
    unit: str = "unit"
    base_reference_value: int = B["default_resource_value"]
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return {
            "definition_id": self.definition_id,
            "name": self.name,
            "unit": self.unit,
            "base_reference_value": self.base_reference_value,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResourceDefinition":
        return cls(
            definition_id=str(data["definition_id"]),
            name=str(data["name"]),
            unit=str(data.get("unit", "unit")),
            base_reference_value=int(data.get("base_reference_value", 1)),
            provenance=str(data.get("provenance", "GAME_EXTENSION")),
        )


@dataclass
class ResourceLot:
    lot_id: str
    definition_id: str
    quantity: int
    quality: int
    owner_id: str
    location_id: str
    source_node_id: str | None = None
    freshness_hours: int = 0

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("resource lot quantity must be positive")
        if self.quality <= 0:
            raise ValueError("resource lot quality must be positive")

    def to_dict(self) -> dict[str, Any]:
        return {
            "lot_id": self.lot_id,
            "definition_id": self.definition_id,
            "quantity": self.quantity,
            "quality": self.quality,
            "owner_id": self.owner_id,
            "location_id": self.location_id,
            "source_node_id": self.source_node_id,
            "freshness_hours": self.freshness_hours,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResourceLot":
        return cls(
            lot_id=str(data["lot_id"]),
            definition_id=str(data["definition_id"]),
            quantity=int(data["quantity"]),
            quality=int(data["quality"]),
            owner_id=str(data["owner_id"]),
            location_id=str(data["location_id"]),
            source_node_id=data.get("source_node_id"),
            freshness_hours=int(data.get("freshness_hours", 0)),
        )


@dataclass
class ResourceNode:
    node_id: str
    location_id: str
    resource_definition_id: str
    current_stock: int
    carrying_capacity: int
    regeneration_per_hour: int
    extraction_pressure: int = 0
    regeneration_remainder: int = 0
    provenance: str = "GAME_EXTENSION"

    def __post_init__(self) -> None:
        if not 0 <= self.current_stock <= self.carrying_capacity:
            raise ValueError("resource node stock must fit its capacity")
        if self.regeneration_per_hour < 0:
            raise ValueError("regeneration_per_hour cannot be negative")

    def regenerate(self, seconds: int) -> int:
        if seconds < 0:
            raise ValueError("regeneration seconds cannot be negative")
        total = self.regeneration_remainder + seconds * self.regeneration_per_hour
        units, self.regeneration_remainder = divmod(total, 3_600)
        before = self.current_stock
        self.current_stock = min(
            self.carrying_capacity,
            self.current_stock + units,
        )
        return self.current_stock - before

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "location_id": self.location_id,
            "resource_definition_id": self.resource_definition_id,
            "current_stock": self.current_stock,
            "carrying_capacity": self.carrying_capacity,
            "regeneration_per_hour": self.regeneration_per_hour,
            "extraction_pressure": self.extraction_pressure,
            "regeneration_remainder": self.regeneration_remainder,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResourceNode":
        return cls(
            node_id=str(data["node_id"]),
            location_id=str(data["location_id"]),
            resource_definition_id=str(data["resource_definition_id"]),
            current_stock=int(data["current_stock"]),
            carrying_capacity=int(data["carrying_capacity"]),
            regeneration_per_hour=int(data["regeneration_per_hour"]),
            extraction_pressure=int(data.get("extraction_pressure", 0)),
            regeneration_remainder=int(data.get("regeneration_remainder", 0)),
            provenance=str(data.get("provenance", "GAME_EXTENSION")),
        )


@dataclass
class GuDefinition:
    definition_id: str
    name: str
    rank: int
    food_definition_id: str
    feed_quantity: int = B["gu_feed_quantity"]
    hunger_per_hour: int = B["gu_hunger_per_hour"]
    satiety_maximum: int = B["gu_satiety_max"]
    provenance: str = "GAME_EXTENSION"

    def to_dict(self) -> dict[str, Any]:
        return {
            "definition_id": self.definition_id,
            "name": self.name,
            "rank": self.rank,
            "food_definition_id": self.food_definition_id,
            "feed_quantity": self.feed_quantity,
            "hunger_per_hour": self.hunger_per_hour,
            "satiety_maximum": self.satiety_maximum,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GuDefinition":
        return cls(
            definition_id=str(data["definition_id"]),
            name=str(data["name"]),
            rank=int(data["rank"]),
            food_definition_id=str(data["food_definition_id"]),
            feed_quantity=int(data.get("feed_quantity", B["gu_feed_quantity"])),
            hunger_per_hour=int(data.get("hunger_per_hour", B["gu_hunger_per_hour"])),
            satiety_maximum=int(data.get("satiety_maximum", B["gu_satiety_max"])),
            provenance=str(data.get("provenance", "GAME_EXTENSION")),
        )


@dataclass
class GuInstance:
    instance_id: str
    definition_id: str
    owner_id: str
    rank: int
    satiety: int
    hunger_state: HungerState = HungerState.NORMAL
    condition: int = B["default_gu_condition"]
    hunger_remainder: int = 0

    def update_hunger(self, seconds: int, definition: GuDefinition) -> tuple[int, HungerState]:
        old_satiety = self.satiety
        old_state = self.hunger_state
        total = self.hunger_remainder + seconds * definition.hunger_per_hour
        loss, self.hunger_remainder = divmod(total, 3_600)
        self.satiety = max(0, self.satiety - loss)
        self.hunger_state = self.derive_hunger_state(self.satiety, definition.satiety_maximum)
        return old_satiety, old_state

    @staticmethod
    def derive_hunger_state(satiety: int, maximum: int) -> HungerState:
        ratio = satiety / maximum if maximum else 0
        if ratio >= 0.9:
            return HungerState.FULL
        if ratio >= 0.5:
            return HungerState.NORMAL
        if ratio >= 0.2:
            return HungerState.HUNGRY
        if satiety > 0:
            return HungerState.STARVING
        return HungerState.CRITICAL

    def to_dict(self) -> dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "definition_id": self.definition_id,
            "owner_id": self.owner_id,
            "rank": self.rank,
            "satiety": self.satiety,
            "hunger_state": self.hunger_state.value,
            "condition": self.condition,
            "hunger_remainder": self.hunger_remainder,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GuInstance":
        return cls(
            instance_id=str(data["instance_id"]),
            definition_id=str(data["definition_id"]),
            owner_id=str(data["owner_id"]),
            rank=int(data["rank"]),
            satiety=int(data["satiety"]),
            hunger_state=HungerState(data.get("hunger_state", HungerState.NORMAL.value)),
            condition=int(data.get("condition", 100)),
            hunger_remainder=int(data.get("hunger_remainder", 0)),
        )


@dataclass
class LocalMarket:
    market_id: str
    location_id: str
    currency: int
    inventory: dict[str, ResourceLot] = field(default_factory=dict)
    base_prices: dict[str, int] = field(default_factory=dict)
    price_adjustments: dict[str, int] = field(default_factory=dict)
    max_price_shift: int = B["market_max_price_shift"]
    price_provenance: str = "GAME_EXTENSION"

    def price_for(self, definition_id: str) -> int:
        base = self.base_prices.get(definition_id, 1)
        adjustment = self.price_adjustments.get(definition_id, 0)
        return max(1, base + adjustment)

    def inventory_quantity(self, definition_id: str) -> int:
        return sum(
            lot.quantity for lot in self.inventory.values() if lot.definition_id == definition_id
        )

    def apply_buy_pressure(self, definition_id: str) -> None:
        current = self.price_adjustments.get(definition_id, 0)
        self.price_adjustments[definition_id] = min(self.max_price_shift, current + 1)

    def apply_sell_pressure(self, definition_id: str) -> None:
        current = self.price_adjustments.get(definition_id, 0)
        self.price_adjustments[definition_id] = max(-self.max_price_shift, current - 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "market_id": self.market_id,
            "location_id": self.location_id,
            "currency": self.currency,
            "inventory": [lot.to_dict() for lot in self.inventory.values()],
            "base_prices": self.base_prices,
            "price_adjustments": self.price_adjustments,
            "max_price_shift": self.max_price_shift,
            "price_provenance": self.price_provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalMarket":
        lots = [ResourceLot.from_dict(item) for item in data.get("inventory", [])]
        return cls(
            market_id=str(data["market_id"]),
            location_id=str(data["location_id"]),
            currency=int(data["currency"]),
            inventory={lot.lot_id: lot for lot in lots},
            base_prices={str(key): int(value) for key, value in data.get("base_prices", {}).items()},
            price_adjustments={
                str(key): int(value) for key, value in data.get("price_adjustments", {}).items()
            },
            max_price_shift=int(data.get("max_price_shift", B["market_max_price_shift"])),
            price_provenance=str(data.get("price_provenance", "GAME_EXTENSION")),
        )


@dataclass
class Character:
    character_id: str
    name: str
    controller: Controller
    location_id: str
    currency: int
    cultivation: CultivationState
    inventory: dict[str, ResourceLot] = field(default_factory=dict)
    owned_gu_ids: list[str] = field(default_factory=list)
    action_count: int = 0

    def inventory_quantity(self, definition_id: str) -> int:
        return sum(
            lot.quantity for lot in self.inventory.values() if lot.definition_id == definition_id
        )

    def add_lot(self, lot: ResourceLot) -> None:
        if lot.owner_id != self.character_id:
            raise ValueError("resource lot owner does not match inventory owner")
        self.inventory[lot.lot_id] = lot

    def to_dict(self) -> dict[str, Any]:
        return {
            "character_id": self.character_id,
            "name": self.name,
            "controller": self.controller.value,
            "location_id": self.location_id,
            "currency": self.currency,
            "cultivation": self.cultivation.to_dict(),
            "inventory": [lot.to_dict() for lot in self.inventory.values()],
            "owned_gu_ids": list(self.owned_gu_ids),
            "action_count": self.action_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Character":
        lots = [ResourceLot.from_dict(item) for item in data.get("inventory", [])]
        return cls(
            character_id=str(data["character_id"]),
            name=str(data["name"]),
            controller=Controller(data["controller"]),
            location_id=str(data["location_id"]),
            currency=int(data["currency"]),
            cultivation=CultivationState.from_dict(data["cultivation"]),
            inventory={lot.lot_id: lot for lot in lots},
            owned_gu_ids=[str(item) for item in data.get("owned_gu_ids", [])],
            action_count=int(data.get("action_count", 0)),
        )


@dataclass(frozen=True)
class ActionIntent:
    action_type: ActionType
    actor_id: str
    resource_id: str | None = None
    quantity: int = 0
    gu_id: str | None = None
    duration_seconds: int | None = None
    target_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type.value,
            "actor_id": self.actor_id,
            "resource_id": self.resource_id,
            "quantity": self.quantity,
            "gu_id": self.gu_id,
            "duration_seconds": self.duration_seconds,
            "target_id": self.target_id,
        }


@dataclass(frozen=True)
class ActionResult:
    success: bool
    action_type: ActionType
    actor_id: str
    message: str
    event_ids: tuple[str, ...] = ()
    elapsed_seconds: int = 0
