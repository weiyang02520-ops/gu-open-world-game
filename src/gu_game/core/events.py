"""Domain events and an explicit publish/dispatch event bus."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Deque, Iterable


class EventVisibility(StrEnum):
    PUBLIC = "PUBLIC"
    ACTOR_ONLY = "ACTOR_ONLY"
    OBSERVERS = "OBSERVERS"


@dataclass(frozen=True)
class DomainEvent:
    """An immutable event envelope; reducers may interpret its payload later."""

    event_id: str
    event_type: str
    timestamp: int
    actor_id: str | None = None
    target_ids: tuple[str, ...] = ()
    location_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    visibility: EventVisibility = EventVisibility.PUBLIC
    source: str | None = None
    provenance: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id or not self.event_type:
            raise ValueError("event_id and event_type are required")
        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")
        object.__setattr__(self, "target_ids", tuple(self.target_ids))
        object.__setattr__(self, "payload", dict(self.payload))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "actor_id": self.actor_id,
            "target_ids": list(self.target_ids),
            "location_id": self.location_id,
            "payload": self.payload,
            "visibility": self.visibility.value,
            "source": self.source,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DomainEvent":
        return cls(
            event_id=str(data["event_id"]),
            event_type=str(data["event_type"]),
            timestamp=int(data["timestamp"]),
            actor_id=data.get("actor_id"),
            target_ids=tuple(data.get("target_ids", ())),
            location_id=data.get("location_id"),
            payload=dict(data.get("payload", {})),
            visibility=EventVisibility(data.get("visibility", EventVisibility.PUBLIC.value)),
            source=data.get("source"),
            provenance=data.get("provenance"),
        )


EventHandler = Callable[[DomainEvent], None]


class EventBus:
    """Queue events, preserve history, and dispatch handlers explicitly."""

    def __init__(self) -> None:
        self._queue: Deque[DomainEvent] = deque()
        self._history: list[DomainEvent] = []
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    @property
    def history(self) -> tuple[DomainEvent, ...]:
        return tuple(self._history)

    @property
    def pending_count(self) -> int:
        return len(self._queue)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if not event_type:
            raise ValueError("event_type is required")
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        self._queue.append(event)
        self._history.append(event)

    def dispatch_pending(self) -> int:
        dispatched = 0
        while self._queue:
            event = self._queue.popleft()
            handlers: Iterable[EventHandler] = (
                *self._handlers.get(event.event_type, ()),
                *self._handlers.get("*", ()),
            )
            for handler in handlers:
                handler(event)
            dispatched += 1
        return dispatched
