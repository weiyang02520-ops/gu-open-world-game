"""Dynamic playable-layer events and their serializable consequences.

The early prototype represented a pending event by its display title and then
generated a *different* event while resolving it.  That made a save taken
between generation and player choice impossible to resume faithfully.  This
module keeps the complete :class:`WorldEvent` as the pending record and uses a
single ``Effect`` representation for all player and world changes.

The functions intentionally accept a small duck-typed RNG interface.  M1's
``DeterministicRNG`` can therefore be supplied by the integrated simulation,
while callers of the old four-argument prototype API continue to work without
touching Python's process-global random generator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Any, Iterable, Mapping, Sequence


def _stable_fraction(*parts: object) -> float:
    """Return a repeatable value in ``[0, 1)`` without global RNG state."""

    key = "\x1f".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(key).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def _stable_index(length: int, *parts: object) -> int:
    if length <= 0:
        raise ValueError("length must be positive")
    key = "\x1f".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big") % length


@dataclass(frozen=True)
class Effect:
    """One state change produced by an event."""

    target: str
    attribute: str
    change: int | float | str
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.target:
            raise ValueError("effect target is required")
        if not self.attribute:
            raise ValueError("effect attribute is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "attribute": self.attribute,
            "change": self.change,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Effect":
        return cls(
            target=str(data["target"]),
            attribute=str(data["attribute"]),
            change=data.get("change", 0),
            reason=str(data.get("reason", "")),
        )


@dataclass
class EventResult:
    """Serializable consequence bundle.

    ``description`` and the old resource/danger/health fields are kept for
    compatibility with the first playable prototype.  New consumers should
    read ``effects``; ``to_dict`` always emits both normalized effects and
    compatibility maps so old save files remain readable.
    """

    description: str = ""
    resource_changes: dict[str, int] = field(default_factory=dict)
    danger_change: int = 0
    health_change: int = 0
    effects: list[Effect] = field(default_factory=list)
    player_changes: dict[str, int] = field(default_factory=dict)
    world_changes: dict[str, int] = field(default_factory=dict)
    message: str | None = None

    def __post_init__(self) -> None:
        if self.message is None:
            self.message = self.description
        elif not self.description:
            self.description = self.message
        if not self.effects:
            normalized: list[Effect] = []
            for attribute, change in self.player_changes.items():
                normalized.append(Effect("player", str(attribute), change, "event choice"))
            for attribute, change in self.world_changes.items():
                normalized.append(Effect("world", str(attribute), change, "event choice"))
            for resource, change in self.resource_changes.items():
                normalized.append(Effect("player", f"resource:{resource}", change, "event choice"))
            if self.health_change:
                normalized.append(Effect("player", "health", self.health_change, "event choice"))
            if self.danger_change:
                normalized.append(Effect("world", "danger", self.danger_change, "event choice"))
            self.effects = normalized

    @property
    def all_effects(self) -> tuple[Effect, ...]:
        return tuple(self.effects)

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "message": self.message,
            "resource_changes": dict(self.resource_changes),
            "danger_change": self.danger_change,
            "health_change": self.health_change,
            "player_changes": dict(self.player_changes),
            "world_changes": dict(self.world_changes),
            "effects": [effect.to_dict() for effect in self.effects],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EventResult":
        return cls(
            description=str(data.get("description", data.get("message", ""))),
            message=data.get("message"),
            resource_changes={str(k): int(v) for k, v in data.get("resource_changes", {}).items()},
            danger_change=int(data.get("danger_change", 0)),
            health_change=int(data.get("health_change", 0)),
            player_changes={str(k): int(v) for k, v in data.get("player_changes", {}).items()},
            world_changes={str(k): int(v) for k, v in data.get("world_changes", {}).items()},
            effects=[Effect.from_dict(item) for item in data.get("effects", [])],
        )


@dataclass
class WorldEvent:
    """A complete pending event record.

    The first four fields retain the original positional constructor.  New
    fields make events self-contained: a generated event can be written to a
    save file and later resolved without re-rolling its title or options.
    """

    event_type: str
    title: str
    danger: int
    options: list[str] = field(default_factory=list)
    event_id: str = ""
    location: str = ""
    day: int = 1
    source: str = "dynamic_world"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.event_type = str(self.event_type)
        self.title = str(self.title)
        self.danger = max(0, min(100, int(self.danger)))
        self.options = [str(option) for option in self.options]
        self.location = str(self.location)
        self.day = max(1, int(self.day))
        if not self.event_id:
            self.event_id = self.make_id(
                self.event_type,
                self.title,
                self.location,
                self.day,
                self.danger,
                ",".join(self.options),
            )

    @staticmethod
    def make_id(*parts: object) -> str:
        key = "\x1f".join(str(part) for part in parts).encode("utf-8")
        return f"event-{hashlib.sha256(key).hexdigest()[:20]}"

    @property
    def id(self) -> str:
        return self.event_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "id": self.event_id,
            "event_type": self.event_type,
            "type": self.event_type,
            "title": self.title,
            "danger": self.danger,
            "options": list(self.options),
            "location": self.location,
            "day": self.day,
            "source": self.source,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WorldEvent":
        return cls(
            event_type=str(data.get("event_type", data.get("type", "unknown"))),
            title=str(data.get("title", "未知事件")),
            danger=int(data.get("danger", 0)),
            options=[str(item) for item in data.get("options", [])],
            event_id=str(data.get("event_id", data.get("id", ""))),
            location=str(data.get("location", "")),
            day=int(data.get("day", 1)),
            source=str(data.get("source", "dynamic_world")),
            metadata=dict(data.get("metadata", {})),
        )


EVENT_POOL: dict[str, list[WorldEvent]] = {
    "荒林": [
        WorldEvent("resource", "发现残留蛊材气息", 25, ["采集", "观察", "离开"]),
        WorldEvent("beast", "遭遇野兽活动痕迹", 45, ["追踪", "避开", "设伏"]),
    ],
    "山洞": [
        WorldEvent("unknown", "发现未知洞穴入口", 70, ["探索", "记录", "撤退"])
    ],
    "村庄": [
        WorldEvent("rumor", "村民流传附近异常消息", 10, ["调查", "询问", "忽略"])
    ],
    "坊市": [
        WorldEvent("merchant", "商旅带来边地消息", 15, ["交易", "打听", "离开"])
    ],
}


def _rng_random(rng: Any, *parts: object) -> float:
    if rng is None:
        return _stable_fraction(*parts)
    method = getattr(rng, "random", None)
    if callable(method):
        return float(method())
    return _stable_fraction(*parts)


def _rng_index(rng: Any, values: Sequence[Any], *parts: object) -> int:
    if not values:
        raise IndexError("cannot choose from an empty sequence")
    if rng is not None:
        method = getattr(rng, "choice", None)
        if callable(method):
            chosen = method(values)
            return values.index(chosen)
    return _stable_index(len(values), *parts)


def generate_event(
    location: str,
    danger_level: int,
    rng: Any = None,
    *,
    resources: Mapping[str, int] | None = None,
    npc_states: Iterable[Any] | None = None,
    player_history: Iterable[str] | None = None,
    day: int = 1,
) -> WorldEvent | None:
    """Generate one deterministic event from current world context."""

    location = str(location)
    danger_level = max(0, min(100, int(danger_level)))
    context_resources = dict(resources or {})
    npc_list = list(npc_states or ())
    history_tail = list(player_history or ())[-3:]
    context_key = (
        location,
        danger_level,
        day,
        tuple(sorted(context_resources.items())),
        len(npc_list),
        tuple(history_tail),
    )
    chance = min(0.2 + danger_level / 300.0, 0.8)
    if _rng_random(rng, "event-chance", *context_key) > chance:
        return None

    candidates = list(EVENT_POOL.get(location, ()))
    if not candidates:
        candidates = [WorldEvent("unknown", "环境出现异常迹象", danger_level, ["观察", "撤退"])]
    if context_resources and all(value <= 0 for value in context_resources.values()):
        candidates.append(WorldEvent("shortage", "附近资源已经枯竭", danger_level, ["调查", "离开"]))
    if any(
        (
            getattr(npc, "goal", None)
            if not isinstance(npc, Mapping)
            else npc.get("goal")
        )
        in {"trade", "交易"}
        for npc in npc_list
    ):
        candidates.append(WorldEvent("npc", "遇到正在赶路的商人", danger_level, ["交谈", "跟随", "离开"]))
    index = _rng_index(rng, candidates, "event-kind", *context_key)
    template = candidates[index]
    event_id = WorldEvent.make_id(template.event_type, template.title, location, day, danger_level, index, context_key)
    metadata = {
        "resource_snapshot": {str(k): int(v) for k, v in context_resources.items()},
        "npc_count": len(npc_list),
        "history_tail": history_tail,
    }
    return WorldEvent(
        event_type=template.event_type,
        title=template.title,
        danger=max(template.danger, danger_level if template.event_type in {"shortage", "unknown"} else template.danger),
        options=list(template.options),
        event_id=event_id,
        location=location,
        day=day,
        metadata=metadata,
    )


def resolve_event(event: WorldEvent, choice: str) -> EventResult:
    """Convert a pending event and one choice into normalized effects."""

    choice = str(choice)
    if choice not in event.options:
        return EventResult("未知选择，事件暂时搁置。", message="未知选择，事件暂时搁置。")

    effects: list[Effect] = []
    resource_changes: dict[str, int] = {}
    danger_change = 0
    health_change = 0
    description = f"你选择了{choice}，事件【{event.title}】暂时结束。"

    if event.event_type == "resource" and choice == "采集":
        description = "成功采集蛊材。"
        resource_changes = {"月兰草": 2}
        effects.append(Effect("player", "resource:月兰草", 2, "采集野外蛊材"))
    elif event.event_type == "beast" and choice == "追踪":
        description = "发现兽材，但受到野兽攻击。"
        resource_changes = {"兽材": 1}
        health_change = -10
        effects.extend(
            [
                Effect("player", "resource:兽材", 1, "追踪野兽痕迹"),
                Effect("player", "health", -10, "受到野兽攻击"),
            ]
        )
    elif event.event_type == "beast" and choice == "设伏":
        description = "成功伏击野兽。"
        resource_changes = {"兽材": 2}
        effects.append(Effect("player", "resource:兽材", 2, "伏击野兽"))
    elif event.event_type == "unknown" and choice == "探索":
        description = "洞穴深处发现未知资源，同时危险增加。"
        resource_changes = {"未知蛊材": 1}
        danger_change = 5
        effects.extend(
            [
                Effect("player", "resource:未知蛊材", 1, "探索洞穴"),
                Effect("world", "danger", 5, "洞穴探索惊动环境"),
            ]
        )
    elif event.event_type == "rumor" and choice in ("调查", "询问"):
        description = "获得附近区域情报。"
        danger_change = -2
        effects.append(Effect("world", "danger", -2, "核实村庄消息"))
    elif event.event_type == "merchant" and choice == "交易":
        description = "你与商旅完成一次小额交易。"
        effects.append(Effect("player", "yuan_stones", 1, "商旅交易"))
    elif event.event_type == "merchant" and choice == "打听":
        description = "你从商旅处获得了新的路线情报。"
        effects.append(Effect("world", "danger", -1, "商旅情报降低路线风险"))
    elif event.event_type == "shortage" and choice == "调查":
        description = "你确认了资源短缺的范围。"
        effects.append(Effect("world", "danger", 2, "短缺调查暴露行踪"))
        danger_change = 2
    elif event.event_type == "npc" and choice == "交谈":
        description = "你与商人交谈，记下了他的路线。"
        effects.append(Effect("player", "information", 1, "与商人交谈"))

    if effects and not resource_changes:
        resource_changes = {
            effect.attribute.removeprefix("resource:"): int(effect.change)
            for effect in effects
            if effect.target == "player" and effect.attribute.startswith("resource:") and isinstance(effect.change, (int, float))
        }
    if effects and not danger_change:
        danger_change = sum(
            int(effect.change)
            for effect in effects
            if effect.target == "world" and effect.attribute == "danger" and isinstance(effect.change, (int, float))
        )
    if effects and not health_change:
        health_change = sum(
            int(effect.change)
            for effect in effects
            if effect.target == "player" and effect.attribute == "health" and isinstance(effect.change, (int, float))
        )
    return EventResult(
        description=description,
        resource_changes=resource_changes,
        danger_change=danger_change,
        health_change=health_change,
        effects=effects,
        message=description,
    )


def serialize_pending_events(events: Iterable[WorldEvent]) -> list[dict[str, Any]]:
    """Serialize a pending-event queue without reducing it to titles."""

    return [event.to_dict() for event in events]


def deserialize_pending_events(data: Iterable[Mapping[str, Any]]) -> list[WorldEvent]:
    return [WorldEvent.from_dict(item) for item in data]


__all__ = [
    "Effect",
    "EventResult",
    "WorldEvent",
    "EVENT_POOL",
    "generate_event",
    "resolve_event",
    "serialize_pending_events",
    "deserialize_pending_events",
]
