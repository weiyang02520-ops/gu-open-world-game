"""V0.1 dynamic world events and consequence resolution.

Events are generated from world state instead of fixed story scripts.
This layer converts player choices into deterministic world changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random


@dataclass
class EventResult:
    description: str
    resource_changes: dict[str, int] = field(default_factory=dict)
    danger_change: int = 0
    health_change: int = 0


@dataclass
class WorldEvent:
    event_type: str
    title: str
    danger: int
    options: list[str] = field(default_factory=list)


EVENT_POOL = {
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
}


def generate_event(location: str, danger_level: int) -> WorldEvent | None:
    """Generate an event using location and world danger."""
    if random.random() > min(0.2 + danger_level / 300, 0.8):
        return None

    candidates = EVENT_POOL.get(location, [])
    if not candidates:
        return None

    return random.choice(candidates)


def resolve_event(event: WorldEvent, choice: str) -> EventResult:
    """Convert an event choice into actual world consequences."""
    if choice not in event.options:
        return EventResult("未知选择，事件暂时搁置。")

    if event.event_type == "resource" and choice == "采集":
        return EventResult(
            "成功采集蛊材。",
            resource_changes={"月兰草": 2},
        )

    if event.event_type == "beast" and choice == "追踪":
        return EventResult(
            "发现兽材，但受到野兽攻击。",
            resource_changes={"兽材": 1},
            health_change=-10,
        )

    if event.event_type == "beast" and choice == "设伏":
        return EventResult(
            "成功伏击野兽。",
            resource_changes={"兽材": 2},
        )

    if event.event_type == "unknown" and choice == "探索":
        return EventResult(
            "洞穴深处发现未知资源，同时危险增加。",
            resource_changes={"未知蛊材": 1},
            danger_change=5,
        )

    if event.event_type == "rumor" and choice in ("调查", "询问"):
        return EventResult("获得附近区域情报。", danger_change=-2)

    return EventResult(f"你选择了{choice}，事件【{event.title}】暂时结束。")
