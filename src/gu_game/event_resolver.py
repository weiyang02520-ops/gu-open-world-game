"""Apply dynamic event choices through one serializable Effect interface.

``EventResolver`` accepts either a pending :class:`WorldEvent` or one of the
small legacy event identifiers used by the first playable prototype.  The
choice is resolved against the event record itself; callers never need to
re-roll an event after loading a save.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .event_system import Effect, EventResult, WorldEvent, resolve_event


LEGACY_EVENTS: dict[str, WorldEvent] = {
    "wild_gu_material": WorldEvent(
        "resource", "发现野外蛊材", 25, ["collect", "observe", "leave"],
        event_id="wild_gu_material", location="荒林",
    ),
    "beast_trace": WorldEvent(
        "beast", "发现野兽痕迹", 45, ["avoid", "track"],
        event_id="beast_trace", location="荒林",
    ),
}


class EventResolver:
    """Resolve and optionally apply effects to duck-typed game state objects."""

    def __init__(self, *, effect_applier: Any = None) -> None:
        self.effect_applier = effect_applier

    def resolve(self, event: WorldEvent | Mapping[str, Any] | str, choice: str) -> EventResult:
        """Resolve a pending event without mutating world state."""

        if isinstance(event, str):
            pending = LEGACY_EVENTS.get(event)
            if pending is None:
                return EventResult("事件没有产生明显变化。", message="事件没有产生明显变化。")
            # Legacy English options map onto the bilingual event rules while
            # preserving the identifier in the resulting audit metadata.
            if event == "wild_gu_material":
                if choice == "collect":
                    return EventResult(
                        message="你采集到了少量野外蛊材。",
                        player_changes={"resource:蛊材": 1},
                        world_changes={"荒林资源": -1},
                        effects=[
                            Effect("player", "resource:蛊材", 1, "采集野外蛊材"),
                            Effect("world", "荒林资源", -1, "采集野外蛊材"),
                        ],
                    )
                if choice == "observe":
                    return EventResult(
                        message="你观察环境，发现附近危险正在增加。",
                        world_changes={"danger": 2},
                        effects=[Effect("world", "danger", 2, "观察环境")],
                    )
                if choice == "leave":
                    return EventResult(message="你谨慎离开，没有引起额外注意。")
            if event == "beast_trace":
                if choice == "avoid":
                    return EventResult(message="你避开了野兽活动区域。")
                if choice == "track":
                    return EventResult(
                        message="你追踪野兽痕迹，获得少量兽材线索。",
                        player_changes={"resource:兽材": 1},
                        world_changes={"danger": 1},
                        effects=[
                            Effect("player", "resource:兽材", 1, "追踪野兽痕迹"),
                            Effect("world", "danger", 1, "追踪野兽痕迹"),
                        ],
                    )
            return EventResult(message="事件没有产生明显变化。")

        if isinstance(event, Mapping):
            event = WorldEvent.from_dict(event)
        if not isinstance(event, WorldEvent):
            raise TypeError("event must be a WorldEvent, mapping, or event id")
        return resolve_event(event, choice)

    def apply(
        self,
        result: EventResult,
        *,
        player: Any = None,
        world: Any = None,
        npcs: Mapping[str, Any] | list[Any] | None = None,
    ) -> EventResult:
        """Apply every Effect and return the same result for audit logging.

        The method deliberately uses duck typing so it works with both the
        old ``PlayerGuMaster``/``WorldState`` dataclasses and the M1 character
        model.  Unknown attributes are recorded in a mapping when possible,
        rather than silently discarded.
        """

        if self.effect_applier is not None:
            self.effect_applier(result.effects)
            return result
        for effect in result.effects:
            target = self._target(effect.target, player=player, world=world, npcs=npcs)
            if target is None:
                continue
            self._apply_one(target, effect)
        return result

    def resolve_and_apply(
        self,
        event: WorldEvent | Mapping[str, Any] | str,
        choice: str,
        *,
        player: Any = None,
        world: Any = None,
        npcs: Mapping[str, Any] | list[Any] | None = None,
    ) -> EventResult:
        result = self.resolve(event, choice)
        return self.apply(result, player=player, world=world, npcs=npcs)

    @staticmethod
    def _target(target_name: str, *, player: Any, world: Any, npcs: Any) -> Any:
        if target_name in {"player", "character", "actor"}:
            return player
        if target_name in {"world", "environment"}:
            return world
        if target_name.startswith("npc:"):
            npc_id = target_name.split(":", 1)[1]
            if isinstance(npcs, Mapping):
                return npcs.get(npc_id)
            for npc in npcs or ():
                if getattr(npc, "npc_id", getattr(npc, "id", None)) == npc_id:
                    return npc
        return None

    @staticmethod
    def _apply_one(target: Any, effect: Effect) -> None:
        attribute = effect.attribute
        change = effect.change
        if attribute.startswith("resource:"):
            resource_name = attribute.split(":", 1)[1]
            inventory = getattr(target, "inventory", None)
            if inventory is None and isinstance(target, dict):
                inventory = target.setdefault("inventory", {})
            if isinstance(inventory, dict) and isinstance(change, (int, float)):
                inventory[resource_name] = inventory.get(resource_name, 0) + change
            return
        if isinstance(target, dict):
            current = target.get(attribute, 0)
            if isinstance(change, (int, float)) and isinstance(current, (int, float)):
                target[attribute] = current + change
            else:
                target[attribute] = change
            return
        current = getattr(target, attribute, None)
        if isinstance(change, (int, float)) and isinstance(current, (int, float)):
            setattr(target, attribute, current + change)
        elif isinstance(current, list) and isinstance(change, (int, float)):
            # List-valued counters such as information/log entries use the
            # effect reason as their durable, human-readable item.
            current.extend([effect.reason or attribute] * max(0, int(change)))
        elif current is not None or hasattr(target, attribute):
            setattr(target, attribute, change)
        else:
            # M1 models use an explicit ``flags``/``memory`` map for unknown
            # facts.  Keep a best-effort trace for other dataclasses too.
            extras = getattr(target, "event_effects", None)
            if extras is None:
                try:
                    setattr(target, "event_effects", {})
                    extras = target.event_effects
                except Exception:
                    return
            if isinstance(extras, dict):
                extras[attribute] = change


__all__ = ["Effect", "EventResult", "EventResolver", "LEGACY_EVENTS"]
