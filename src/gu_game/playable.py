"""Minimal player-facing loop for V0.1.

This layer intentionally sits above the deterministic simulation modules. It
provides the first human-playable flow without replacing existing milestones.
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
    day: int = 1


ACTIONS = {
    "1": "修炼",
    "2": "探索",
    "3": "炼蛊",
    "4": "查看蛊虫",
    "5": "结束一天",
}


def create_player() -> PlayerGuMaster:
    name = input("蛊师姓名: ").strip() or "无名蛊师"
    origin = input("身份(散修/家族弟子): ").strip() or "散修"
    return PlayerGuMaster(name=name, origin=origin)


def apply_action(player: PlayerGuMaster, action: str) -> str:
    if action == "1":
        player.primeval_essence = min(100, player.primeval_essence + 5)
        return "闭关修炼，真元提升。"
    if action == "2":
        player.yuan_stones += 3
        return "探索外围，获得少量资源。"
    if action == "3":
        if player.yuan_stones >= 5:
            player.yuan_stones -= 5
            return "尝试炼蛊，暂未获得新蛊。"
        return "元石不足，无法炼蛊。"
    if action == "4":
        return "当前蛊虫: " + ", ".join(player.owned_gu)
    if action == "5":
        player.day += 1
        return "时间推进。"
    return "未知行动。"


def run_playable() -> None:
    player = create_player()
    print("进入青茅山外围。")
    while player.day <= 10:
        print(f"\n第 {player.day} 天 | {player.name} | {player.rank}")
        print(f"真元:{player.primeval_essence} 元石:{player.yuan_stones}")
        for key, value in ACTIONS.items():
            print(f"{key}. {value}")
        choice = input("> ").strip()
        print(apply_action(player, choice))
        if choice == "5":
            continue
