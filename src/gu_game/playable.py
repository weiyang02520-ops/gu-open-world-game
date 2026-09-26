"""Player-facing V0.1 playable layer.

A small playable shell over the deterministic simulation core.
The first goal is not visual presentation, but making the 30-day survival
loop testable: player decision -> world feedback -> next day.
"""

from __future__ import annotations

from dataclasses import dataclass, field


LOCATIONS = {
    "村庄": {"danger": 10, "resource": "生活补给"},
    "荒林": {"danger": 45, "resource": "月兰草/兽材"},
    "坊市": {"danger": 15, "resource": "交易"},
    "山洞": {"danger": 70, "resource": "未知蛊材"},
}


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


def world_tick(player: PlayerGuMaster) -> None:
    player.day += 1
    player.action_points = 3
    player.inventory["食物"] = max(0, player.inventory["食物"] - 1)
    player.record("世界推进一天，资源与状态更新。")


def apply_action(player: PlayerGuMaster, action: str) -> str:
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
        result = f"进入荒林探索，发现线索并获得{gain}枚元石。"

    elif action == "3":
        player.inventory["月兰草"] = player.inventory.get("月兰草", 0) + 1
        result = "采集月兰草，可用于蛊虫培养。"

    elif action == "4":
        player.location = "坊市"
        result = "来到坊市，可以交易和获取情报。"

    elif action == "5":
        result = (
            f"地点:{player.location} 境界:{player.rank} "
            f"真元:{player.primeval_essence} 元石:{player.yuan_stones} "
            f"蛊虫:{','.join(player.owned_gu)}"
        )

    elif action == "6":
        player.action_points = 0
        world_tick(player)
        return "结束今日行动，进入下一天。"

    else:
        result = "未知行动。"

    player.record(result)
    return result


def run_playable() -> None:
    player = create_player()
    print("进入青茅山外围，V0.1 Playable Layer 启动。")

    while player.day <= 30:
        print(f"\n第 {player.day} 天 | {player.name} | {player.rank}")
        print(
            f"地点:{player.location} 真元:{player.primeval_essence} "
            f"元石:{player.yuan_stones} 行动点:{player.action_points}"
        )
        for key, value in ACTIONS.items():
            print(f"{key}. {value}")

        choice = input("> ").strip()
        print(apply_action(player, choice))
