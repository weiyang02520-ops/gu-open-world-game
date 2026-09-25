"""Domain events and an explicit publish/dispatch event bus."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Callable, Deque, Iterable, Mapping


class EventVisibility(StrEnum):
    PUBLIC = "PUBLIC"
    ACTOR_ONLY = "ACTOR_ONLY"
    OBSERVERS = "OBSERVERS"


def _freeze(value: Any) -> Any:
    """Recursively freeze event payload values at the durable boundary."""

    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    """Convert a frozen payload back to JSON-compatible containers."""

    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_thaw(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_thaw(item) for item in value)
    return value


@dataclass(frozen=True)
class DomainEvent:
    """An immutable event envelope with a recursively frozen payload."""

    event_id: str
    event_type: str
    timestamp: int
    actor_id: str | None = None
    target_ids: tuple[str, ...] = ()
    location_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    visibility: EventVisibility = EventVisibility.PUBLIC
    source: str | None = None
    provenance: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id or not self.event_type:
            raise ValueError("event_id and event_type are required")
        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")
        object.__setattr__(self, "target_ids", tuple(self.target_ids))
        object.__setattr__(self, "payload", _freeze(dict(self.payload)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "actor_id": self.actor_id,
            "target_ids": list(self.target_ids),
            "location_id": self.location_id,
            "payload": _thaw(self.payload),
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
    """Queue events while exposing one authoritative durable event log.

    Pass ``durable_log`` from ``WorldState.event_log`` for simulation use. In
    that mode ``history`` is a read-only view over the same list, so the bus
    and the save file cannot silently drift apart.
    """

    def __init__(self, durable_log: list[DomainEvent] | None = None) -> None:
        self._queue: Deque[DomainEvent] = deque()
        self._durable_log = durable_log if durable_log is not None else []
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    @property
    def history(self) -> tuple[DomainEvent, ...]:
        return tuple(self._durable_log)

    @property
    def pending_count(self) -> int:
        return len(self._queue)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if not event_type:
            raise ValueError("event_type is required")
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self._durable_log):
            raise ValueError(f"duplicate event_id: {event.event_id}")
        self._queue.append(event)
        self._durable_log.append(event)

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
