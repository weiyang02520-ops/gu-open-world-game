"""Player-facing V0.1 playable layer.

The playable layer is a thin interaction shell above the deterministic world
simulation. It intentionally keeps state simple until full WorldState binding
is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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
    log: list[str] = field(default_factory=list)

    def record(self, message: str) -> None:
        self.log.append(f"Day {self.day}: {message}")


ACTIONS = {
    "1": "修炼",
    "2": "探索",
    "3": "炼蛊",
    "4": "查看状态",
    "5": "结束一天",
}


def create_player() -> PlayerGuMaster:
    name = input("蛊师姓名: ").strip() or "无名蛊师"
    origin = input("身份(散修/家族弟子): ").strip() or "散修"
    return PlayerGuMaster(name=name, origin=origin)


def apply_action(player: PlayerGuMaster, action: str) -> str:
    if action == "1":
        gain = 5
        player.primeval_essence = min(100, player.primeval_essence + gain)
        result = f"闭关修炼，真元+{gain}。"
    elif action == "2":
        gain = 3
        player.yuan_stones += gain
        result = f"探索外围，获得{gain}枚元石。"
    elif action == "3":
        if player.yuan_stones >= 5:
            player.yuan_stones -= 5
            result = "消耗元石尝试炼蛊，但本次未成功。"
        else:
            result = "元石不足，无法炼蛊。"
    elif action == "4":
        result = (
            f"境界:{player.rank} 真元:{player.primeval_essence} "
            f"元石:{player.yuan_stones} 蛊虫:{','.join(player.owned_gu)}"
        )
    elif action == "5":
        player.day += 1
        result = "时间推进，世界进入下一天。"
    else:
        result = "未知行动。"

    player.record(result)
    return result


def run_playable() -> None:
    player = create_player()
    print("进入青茅山外围，V0.1 Playable Layer 启动。")

    while player.day <= 10:
        print(f"\n第 {player.day} 天 | {player.name} | {player.rank}")
        print(f"真元:{player.primeval_essence} 元石:{player.yuan_stones} 气血:{player.health}")
        for key, value in ACTIONS.items():
            print(f"{key}. {value}")

        choice = input("> ").strip()
        print(apply_action(player, choice))

        if choice == "5":
            continue
