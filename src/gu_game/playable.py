"""V0.1 playable layer.

Player loop:
player action -> world feedback -> world tick -> next day.
This is intentionally separated from future UI/network layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random


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

    def tick(self, player: "PlayerGuMaster") -> None:
        self.day += 1
        self.danger_level = min(100, self.danger_level + random.randint(-2, 3))
        self.resources["食物"] = max(0, self.resources["食物"] - 1)
        self.npc_status["巡山弟子"] = "巡逻" if self.day % 2 else "调查"

        if random.random() < 0.25:
            self.events.append("附近出现异常气息，可能存在野外蛊材或危险。")

        player.record(f"世界Tick完成，当前危险度{self.danger_level}。")


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


ACTIONS = {
    "1": "修炼",
    "2": "探索荒林",
    "3": "采集资源",
    "4": "前往坊市",
    "5": "查看状态",
    "6": "结束一天",
}


def create_player() -> PlayerGuMaster:
    name = input("蛊师姓名: ").strip() or "无名蛊师"
    origin = input("身份(散修/家族弟子): ").strip() or "散修"
    return PlayerGuMaster(name=name, origin=origin)


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
        gain = 5
        player.primeval_essence = min(100, player.primeval_essence + gain)
        result = f"静修，真元+{gain}。"

    elif action == "2":
        player.location = "荒林"
        gain = 2
        player.yuan_stones += gain
        result = f"探索荒林，获得{gain}枚元石，并记录附近情报。"

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
        result = (
            f"地点:{player.location} 境界:{player.rank} "
            f"真元:{player.primeval_essence} 元石:{player.yuan_stones} "
            f"世界危险:{world.danger_level}"
        )

    elif action == "6":
        player.action_points = 0
        world_tick(player, world)
        return "结束今日行动，进入下一天。"

    else:
        result = "未知行动。"

    player.record(result)
    return result


def run_playable() -> None:
    player = create_player()
    world = WorldState()
    print("进入青茅山外围，V0.1 Playable Layer 启动。")

    while player.day <= 30:
        print(f"\n第 {player.day} 天 | {player.name} | {player.rank}")
        print(
            f"地点:{player.location} 真元:{player.primeval_essence} "
            f"元石:{player.yuan_stones} 行动点:{player.action_points} "
            f"危险:{world.danger_level}"
        )

        for key, value in ACTIONS.items():
            print(f"{key}. {value}")

        choice = input("> ").strip()
        print(apply_action(player, world, choice))
