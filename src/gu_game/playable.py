"""V0.1 playable layer.

Player loop:
player action -> world feedback -> world tick -> events -> next day.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random

from .event_system import generate_event, resolve_event


LOCATIONS = {
    "村庄": {"danger": 10, "resource": "生活补给"},
    "荒林": {"danger": 45, "resource": "月兰草/兽材"},
    "坊市": {"danger": 15, "resource": "交易"},
    "山洞": {"danger": 70, "resource": "未知蛊材"},
}


@dataclass
class WorldState:
    day: int = 1
    danger_level: int = 20
    resources: dict[str, int] = field(default_factory=lambda: {
        "月兰草": 10,
        "兽材": 5,
        "食物": 20,
    })
    npc_status: dict[str, str] = field(default_factory=lambda: {
        "村民": "正常",
        "巡山弟子": "巡逻",
    })
    events: list[str] = field(default_factory=list)
    history: list[str] = field(default_factory=list)

    def record(self, message: str) -> None:
        self.history.append(f"Day {self.day}: {message}")

    def tick(self, player: "PlayerGuMaster") -> None:
        self.day += 1
        self.danger_level = min(100, self.danger_level + random.randint(-2, 3))
        self.resources["食物"] = max(0, self.resources["食物"] - 1)
        self.npc_status["巡山弟子"] = "巡逻" if self.day % 2 else "调查"

        event = generate_event(player.location, self.danger_level)
        if event:
            self.events.append(event.title)
            self.record(f"发生事件:{event.title}")

        player.record(f"世界Tick完成，危险度{self.danger_level}。")


@dataclass
class PlayerGuMaster:
    name: str
    origin: str
    aptitude: str = "乙等"
    rank: str = "一转初阶"
    primeval_essence: int = 30
    yuan_stones: int = 20
    owned_gu: list[str] = field(default_factory=lambda: ["月光蛊"])
    health: int = 100
    day: int = 1
    location: str = "村庄"
    action_points: int = 3
    inventory: dict[str, int] = field(default_factory=lambda: {"食物": 5})
    log: list[str] = field(default_factory=list)

    def record(self, message: str) -> None:
        self.log.append(f"Day {self.day}: {message}")


def world_tick(player: PlayerGuMaster, world: WorldState) -> None:
    player.day += 1
    player.action_points = 3
    player.inventory["食物"] = max(0, player.inventory.get("食物", 0) - 1)
    world.tick(player)


def apply_action(player: PlayerGuMaster, world: WorldState, action: str) -> str:
    if player.action_points <= 0:
        return "今日行动次数已耗尽，请结束一天。"

    player.action_points -= 1

    if action == "1":
        player.primeval_essence = min(100, player.primeval_essence + 5)
        result = "静修，真元+5。"

    elif action == "2":
        player.location = "荒林"
        player.yuan_stones += 2
        result = "探索荒林，获得元石并寻找线索。"

    elif action == "3":
        if world.resources["月兰草"] > 0:
            world.resources["月兰草"] -= 1
            player.inventory["月兰草"] = player.inventory.get("月兰草", 0) + 1
            result = "采集月兰草成功。"
        else:
            result = "附近月兰草资源不足。"

    elif action == "4":
        player.location = "坊市"
        result = "来到坊市，可以交易和获取情报。"

    elif action == "5":
        result = f"地点:{player.location} 真元:{player.primeval_essence} 元石:{player.yuan_stones} 危险:{world.danger_level}"

    elif action == "6":
        player.action_points = 0
        world_tick(player, world)
        return "结束今日行动，进入下一天。"

    else:
        result = "未知行动。"

    player.record(result)
    return result


def resolve_pending_event(world: WorldState, player: PlayerGuMaster, choice: str) -> str:
    if not world.events:
        return "当前没有待处理事件。"

    title = world.events.pop(0)
    event = generate_event(player.location, 100)
    if not event:
        return "事件已失效。"

    result = resolve_event(event, choice)
    player.health += result.health_change
    world.danger_level = max(0, min(100, world.danger_level + result.danger_change))

    for key, value in result.resource_changes.items():
        world.resources[key] = world.resources.get(key, 0) + value

    world.record(result.description)
    return result.description
