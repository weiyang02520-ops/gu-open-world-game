"""V0.1 dynamic world events.

Events are generated from world state instead of fixed story scripts.
Future versions can connect this layer to quests, factions and combat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random


@dataclass
class WorldEvent:
    event_type: str
    title: str
    danger: int
    options: list[str] = field(default_factory=list)


EVENT_POOL = {
    "荒林": [
        WorldEvent(
            event_type="resource",
            title="发现残留蛊材气息",
            danger=25,
            options=["采集", "观察", "离开"],
        ),
        WorldEvent(
            event_type="beast",
            title="遭遇野兽活动痕迹",
            danger=45,
            options=["追踪", "避开", "设伏"],
        ),
    ],
    "山洞": [
        WorldEvent(
            event_type="unknown",
            title="发现未知洞穴入口",
            danger=70,
            options=["探索", "记录", "撤退"],
        )
    ],
    "村庄": [
        WorldEvent(
            event_type="rumor",
            title="村民流传附近异常消息",
            danger=10,
            options=["调查", "询问", "忽略"],
        )
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


def resolve_event(event: WorldEvent, choice: str) -> str:
    """Temporary resolution layer. Detailed consequences arrive later."""
    if choice not in event.options:
        return "未知选择，事件暂时搁置。"

    return f"你选择了{choice}，事件【{event.title}】产生影响。"
