"""V0.1 event resolution layer.

Converts player choices on generated events into deterministic world changes.
This keeps event generation separate from consequences so future systems
(faction, rumor, economy, combat) can consume the same result model.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EventResult:
    message: str
    player_changes: dict[str, int] = field(default_factory=dict)
    world_changes: dict[str, int] = field(default_factory=dict)


class EventResolver:
    """Resolve V0.1 event choices.

    Future versions can replace this with a larger effect graph without
    changing the event interface.
    """

    def resolve(self, event_id: str, choice: str) -> EventResult:
        if event_id == "wild_gu_material":
            if choice == "collect":
                return EventResult(
                    message="你采集到了少量野外蛊材。",
                    player_changes={"蛊材": 1},
                    world_changes={"荒林资源": -1},
                )
            if choice == "observe":
                return EventResult(
                    message="你观察环境，发现附近危险正在增加。",
                    world_changes={"危险度": 2},
                )
            if choice == "leave":
                return EventResult(message="你谨慎离开，没有引起额外注意。")

        if event_id == "beast_trace":
            if choice == "avoid":
                return EventResult(message="你避开了野兽活动区域。")
            if choice == "track":
                return EventResult(
                    message="你追踪野兽痕迹，获得少量兽材线索。",
                    player_changes={"兽材": 1},
                    world_changes={"危险度": 1},
                )

        return EventResult(message="事件没有产生明显变化。")
