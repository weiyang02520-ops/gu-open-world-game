"""Serializable M5 economy and logistics records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ..m1.models import ResourceLot


class ShipmentStatus(StrEnum):
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    LOST = "LOST"
    CANCELLED = "CANCELLED"


@dataclass
class ResourceNodeCondition:
    node_id: str
    health: int
    environmental_modifier: int = 100
    controller_id: str | None = None
    contested: bool = False
    infrastructure: int = 0
    workers: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.health <= 100:
            raise ValueError("node health must be between 0 and 100")
        if not 0 <= self.environmental_modifier <= 200:
            raise ValueError("environmental modifier must be between 0 and 200")

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResourceNodeCondition":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class MarketBelief:
    actor_id: str
    market_id: str
    believed_prices: dict[str, int] = field(default_factory=dict)
    confidence: int = 50
    last_observed_at: int = 0
    rumors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "market_id": self.market_id,
            "believed_prices": dict(self.believed_prices),
            "confidence": self.confidence,
            "last_observed_at": self.last_observed_at,
            "rumors": list(self.rumors),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketBelief":
        return cls(**data)


@dataclass
class RouteDefinition:
    route_id: str
    origin_market_id: str
    destination_market_id: str
    travel_hours: int
    base_risk: int
    patrol_strength: int = 0
    faction_control: int = 0
    recent_combat: int = 0
    criminal_activity: int = 0
    shortage_pressure: int = 0
    provenance: str = "GAME_EXTENSION"

    def risk_score(self, guards: int = 0) -> int:
        raw = (
            self.base_risk
            + self.recent_combat * 3
            + self.criminal_activity * 2
            + self.shortage_pressure
            - self.patrol_strength
            - self.faction_control // 2
            - guards * 5
        )
        return max(0, min(95, raw))

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RouteDefinition":
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})


@dataclass
class Shipment:
    shipment_id: str
    caravan_id: str
    owner_id: str
    origin_market_id: str
    destination_market_id: str
    route_id: str
    departed_at: int
    arrival_at: int
    cargo: list[ResourceLot]
    guards: int
    risk_at_departure: int
    recipient_faction_id: str | None = None
    status: ShipmentStatus = ShipmentStatus.IN_TRANSIT
    resolved_at: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "shipment_id": self.shipment_id,
            "caravan_id": self.caravan_id,
            "owner_id": self.owner_id,
            "origin_market_id": self.origin_market_id,
            "destination_market_id": self.destination_market_id,
            "route_id": self.route_id,
            "departed_at": self.departed_at,
            "arrival_at": self.arrival_at,
            "cargo": [lot.to_dict() for lot in self.cargo],
            "guards": self.guards,
            "risk_at_departure": self.risk_at_departure,
            "recipient_faction_id": self.recipient_faction_id,
            "status": self.status.value,
            "resolved_at": self.resolved_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Shipment":
        return cls(
            **{
                **data,
                "cargo": [ResourceLot.from_dict(item) for item in data.get("cargo", [])],
                "status": ShipmentStatus(data["status"]),
            }
        )


@dataclass
class Caravan:
    caravan_id: str
    owner_id: str
    route_id: str
    shipment_id: str
    guards: int
    status: ShipmentStatus = ShipmentStatus.IN_TRANSIT

    def to_dict(self) -> dict[str, Any]:
        return {**self.__dict__, "status": self.status.value}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Caravan":
        return cls(**{**data, "status": ShipmentStatus(data["status"])})


@dataclass
class FactionEconomy:
    faction_id: str
    treasury: int
    warehouse: dict[str, ResourceLot] = field(default_factory=dict)
    reserves: dict[str, int] = field(default_factory=dict)
    procurement_orders: list[dict[str, Any]] = field(default_factory=list)
    shortage_intensity: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "faction_id": self.faction_id,
            "treasury": self.treasury,
            "warehouse": [lot.to_dict() for lot in self.warehouse.values()],
            "reserves": dict(self.reserves),
            "procurement_orders": list(self.procurement_orders),
            "shortage_intensity": dict(self.shortage_intensity),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactionEconomy":
        lots = [ResourceLot.from_dict(item) for item in data.get("warehouse", [])]
        return cls(
            faction_id=str(data["faction_id"]),
            treasury=int(data["treasury"]),
            warehouse={lot.lot_id: lot for lot in lots},
            reserves={str(k): int(v) for k, v in data.get("reserves", {}).items()},
            procurement_orders=list(data.get("procurement_orders", [])),
            shortage_intensity={str(k): int(v) for k, v in data.get("shortage_intensity", {}).items()},
        )


@dataclass
class ShortageState:
    resource_id: str
    market_id: str
    demand: int
    stock: int
    severity: int
    started_at: int
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ShortageState":
        return cls(**data)
