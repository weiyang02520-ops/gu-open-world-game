"""Minimal authoritative world state for M0."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .clock import WorldClock
from .events import DomainEvent, EventBus
from .ids import EntityIdFactory
from .rng import DeterministicRNG


@dataclass
class WorldState:
    """State that can be saved and restored without a presentation layer."""

    schema_version: int
    world_seed: int
    clock: WorldClock
    rng: DeterministicRNG
    entity_ids: EntityIdFactory
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)
    event_log: list[DomainEvent] = field(default_factory=list)
    scheduler_queue: list[dict[str, Any]] = field(default_factory=list)
    canon_divergence: list[dict[str, Any]] = field(default_factory=list)
    game_state: dict[str, Any] = field(default_factory=dict)

    CURRENT_SCHEMA_VERSION = 2

    @classmethod
    def new(cls, seed: int) -> "WorldState":
        return cls(
            schema_version=cls.CURRENT_SCHEMA_VERSION,
            world_seed=seed,
            clock=WorldClock(),
            rng=DeterministicRNG(seed),
            entity_ids=EntityIdFactory(),
        )

    def record_event(self, event: DomainEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self.event_log):
            raise ValueError(f"duplicate event_id: {event.event_id}")
        self.event_log.append(event)

    def create_event_bus(self) -> EventBus:
        """Create a bus whose durable history is this state's event log."""

        return EventBus(durable_log=self.event_log)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "world_seed": self.world_seed,
            "world_clock": self.clock.to_dict(),
            "deterministic_rng": self.rng.to_dict(),
            "entity_ids": self.entity_ids.to_dict(),
            "entities": self.entities,
            "event_log": [event.to_dict() for event in self.event_log],
            "scheduler_queue": self.scheduler_queue,
            "canon_divergence": self.canon_divergence,
            "game_state": self.game_state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorldState":
        schema_version = int(data["schema_version"])
        if schema_version > cls.CURRENT_SCHEMA_VERSION:
            raise ValueError(
                f"save schema {schema_version} is newer than supported "
                f"schema {cls.CURRENT_SCHEMA_VERSION}"
            )
        return cls(
            schema_version=schema_version,
            world_seed=int(data["world_seed"]),
            clock=WorldClock.from_dict(data["world_clock"]),
            rng=DeterministicRNG.from_dict(data["deterministic_rng"]),
            entity_ids=EntityIdFactory.from_dict(data["entity_ids"]),
            entities={str(key): dict(value) for key, value in data.get("entities", {}).items()},
            event_log=[DomainEvent.from_dict(item) for item in data.get("event_log", [])],
            scheduler_queue=[dict(item) for item in data.get("scheduler_queue", [])],
            canon_divergence=[dict(item) for item in data.get("canon_divergence", [])],
            game_state=dict(data.get("game_state", {})),
        )
