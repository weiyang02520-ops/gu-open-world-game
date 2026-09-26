"""The V0.1 playable layer.

This module stays headless.  It is the small, stable interface used by a
CLI, a future UI, and save/load tooling while the M1--M8 systems evolve.
The authoritative loop is ``player action -> optional event -> rest/end day
-> world tick``.

The first prototype used process-global :mod:`random`, which made same-seed
runs diverge as soon as another system consumed randomness.  ``WorldState``
now derives every roll from a seed and a serializable counter instead.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .event_resolver import EventResolver
from .event_system import WorldEvent, generate_event, resolve_event
from .npc_sim import NPCSimulation, default_npcs


LOCATIONS: dict[str, dict[str, Any]] = {
    "村庄": {
        "danger": 10,
        "resource": "生活补给",
        "neighbors": ("荒林", "坊市"),
        "npcs": ("村民", "巡山弟子"),
    },
    "荒林": {
        "danger": 45,
        "resource": "月兰草",
        "neighbors": ("村庄", "山洞"),
        "npcs": ("采集者", "野兽"),
    },
    "坊市": {
        "danger": 15,
        "resource": "交易",
        "neighbors": ("村庄",),
        "npcs": ("商人", "散修"),
    },
    "山洞": {
        "danger": 70,
        "resource": "未知蛊材",
        "neighbors": ("荒林",),
        "npcs": ("巡山弟子", "野兽"),
    },
}

PHASES: tuple[str, ...] = ("上午", "下午", "夜晚")
ORIGINS: tuple[str, ...] = ("散修", "家族弟子")
ORIGIN_ALIASES: dict[str, str] = {
    "rogue": "散修",
    "free": "散修",
    "散修": "散修",
    "clan": "家族弟子",
    "family": "家族弟子",
    "家族": "家族弟子",
    "家族弟子": "家族弟子",
}


def _normalise_origin(origin: str | None) -> str:
    if origin is None:
        return "散修"
    value = str(origin).strip()
    return ORIGIN_ALIASES.get(value.casefold(), ORIGIN_ALIASES.get(value, value))


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class WorldState:
    """Serializable state for the headless four-location playable map."""

    day: int = 1
    danger_level: int = 20
    resources: dict[str, int] = field(
        default_factory=lambda: {"月兰草": 10, "兽材": 5, "食物": 20}
    )
    npc_status: dict[str, str] = field(
        default_factory=lambda: {"村民": "正常", "巡山弟子": "巡逻"}
    )
    events: list[str] = field(default_factory=list)
    history: list[str] = field(default_factory=list)
    # Complete event envelopes are retained beside the title list for old UIs.
    event_queue: list[dict[str, Any]] = field(default_factory=list)
    npcs: list[dict[str, Any]] = field(
        default_factory=lambda: [npc.to_dict() for npc in default_npcs()]
    )
    weather: str = "晴"
    economy: dict[str, int] = field(
        default_factory=lambda: {"坊市繁荣度": 50, "食物价格": 2}
    )
    seed: int = 0
    rng_counter: int = 0

    @property
    def world_seed(self) -> int:
        return self.seed

    @property
    def danger(self) -> int:
        return self.danger_level

    @danger.setter
    def danger(self, value: int) -> None:
        self.danger_level = max(0, min(100, int(value)))

    def record(self, message: str) -> None:
        self.history.append(f"Day {self.day}: {message}")

    def _roll(self, label: str, low: int, high: int) -> int:
        if high < low:
            raise ValueError("high must be greater than or equal to low")
        material = f"{self.seed}:{self.rng_counter}:{label}".encode("utf-8")
        digest = hashlib.sha256(material).digest()
        self.rng_counter += 1
        return low + int.from_bytes(digest[:8], "big") % (high - low + 1)

    def _generate_event(self, location: str) -> WorldEvent | None:
        """Call the shared dynamic event interface on a private RNG stream."""

        class _WorldRNG:
            def __init__(self, state: "WorldState") -> None:
                self.state = state

            def random(self) -> float:
                return self.state._roll("event-random", 0, 1_000_000) / 1_000_001

            def choice(self, values: list[Any] | tuple[Any, ...]) -> Any:
                return values[self.state._roll("event-choice", 0, len(values) - 1)]

        return generate_event(
            location,
            self.danger_level,
            _WorldRNG(self),
            resources=self.resources,
            npc_states=self.npcs,
            player_history=self.history,
            day=self.day,
        )

    @staticmethod
    def _event_payload(event: WorldEvent) -> dict[str, Any]:
        return event.to_dict()

    def queue_event(self, event: WorldEvent) -> None:
        payload = self._event_payload(event)
        self.event_queue.append(payload)
        self.events.append(event.title)
        self.record(f"发生事件:{event.title}")

    def pop_event(self) -> WorldEvent | None:
        if not self.event_queue:
            return None
        payload = self.event_queue.pop(0)
        if self.events:
            self.events.pop(0)
        return WorldEvent.from_dict(payload)

    def tick(self, player: "PlayerCharacter") -> None:
        """Advance one day and run deterministic weather/NPC/event updates."""

        self.day += 1
        self.danger_level = max(
            0, min(100, self.danger_level + self._roll("danger", -2, 3))
        )
        self.weather = ("晴", "阴", "雨", "雾")[self._roll("weather", 0, 3)]
        self.resources["食物"] = max(0, self.resources.get("食物", 0) - 1)
        self.resources["月兰草"] = min(
            50, self.resources.get("月兰草", 0) + self._roll("regrowth", 0, 2)
        )
        self.npc_status["村民"] = ("采集", "交易", "休息")[
            self._roll("villager", 0, 2)
        ]
        self.npc_status["商人"] = ("移动", "交易", "收集信息")[
            self._roll("merchant", 0, 2)
        ]
        self.npc_status["巡山弟子"] = "巡逻" if self.day % 2 else "调查"
        npc_simulation = NPCSimulation.from_dict({"day": self.day - 1, "npcs": self.npcs})
        npc_simulation.tick(world=self)
        self.npcs = [npc.to_dict() for npc in npc_simulation.npcs]
        for npc in npc_simulation.npcs:
            self.npc_status[npc.name] = npc.status
        prosperity = self.economy.get("坊市繁荣度", 50)
        prosperity = max(0, min(100, prosperity + self._roll("prosperity", -3, 3)))
        self.economy["坊市繁荣度"] = prosperity
        self.economy["食物价格"] = max(1, 3 - prosperity // 50)

        event = self._generate_event(player.location)
        if event is not None:
            self.queue_event(event)
        self.record(
            f"世界Tick完成，天气{self.weather}，危险度{self.danger_level}。"
        )
        player.day = self.day
        player.action_points = 3
        player.phase = PHASES[0]
        player.record(f"世界Tick完成，危险度{self.danger_level}。")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WorldState":
        return cls(
            day=_as_int(data.get("day"), 1),
            danger_level=max(
                0,
                min(100, _as_int(data.get("danger_level", data.get("danger")), 20)),
            ),
            resources={
                str(k): _as_int(v) for k, v in dict(data.get("resources", {})).items()
            }
            or {"月兰草": 10, "兽材": 5, "食物": 20},
            npc_status={
                str(k): str(v) for k, v in dict(data.get("npc_status", {})).items()
            },
            events=[str(item) for item in data.get("events", [])],
            history=[str(item) for item in data.get("history", [])],
            event_queue=[dict(item) for item in data.get("event_queue", [])],
            npcs=[dict(item) for item in data.get("npcs", [])]
            or [npc.to_dict() for npc in default_npcs()],
            weather=str(data.get("weather", "晴")),
            economy={
                str(k): _as_int(v)
                for k, v in dict(data.get("economy", {})).items()
            }
            or {"坊市繁荣度": 50, "食物价格": 2},
            seed=_as_int(data.get("seed", data.get("world_seed", 0))),
            rng_counter=_as_int(data.get("rng_counter"), 0),
        )


@dataclass
class PlayerCharacter:
    """The player-facing character record used by the V0.1 loop."""

    name: str
    origin: str = "散修"
    aptitude: str = "乙等"
    rank: str = "一转初阶"
    primeval_essence: int = 30
    health: int = 100
    owned_gu: list[str] = field(default_factory=lambda: ["月光蛊"])
    location: str = "村庄"
    yuan_stones: int = 20
    inventory: dict[str, int] = field(default_factory=lambda: {"食物": 5})
    day: int = 1
    action_points: int = 3
    phase: str = "上午"
    cultivation_progress: int = 0
    discovered_locations: list[str] = field(default_factory=lambda: ["村庄"])
    information: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    id: str = "player-1"

    @classmethod
    def create(
        cls,
        name: str,
        origin: str = "散修",
        *,
        seed: int | None = None,
        player_id: str | None = None,
    ) -> "PlayerCharacter":
        """Create a deterministic starting character."""

        normalised = _normalise_origin(origin)
        if normalised not in ORIGINS:
            raise ValueError(f"unsupported origin: {origin}")
        suffix = abs(_as_int(seed, 1)) if seed is not None else 1
        if normalised == "家族弟子":
            return cls(
                name=str(name),
                origin=normalised,
                aptitude="甲等",
                primeval_essence=35,
                yuan_stones=30,
                inventory={"食物": 8, "月兰草": 1},
                id=player_id or f"player-{suffix}",
            )
        return cls(
            name=str(name),
            origin=normalised,
            aptitude="乙等",
            primeval_essence=30,
            yuan_stones=20,
            inventory={"食物": 5},
            id=player_id or f"player-{suffix}",
        )

    @property
    def character_id(self) -> str:
        return self.id

    @property
    def gu_inventory(self) -> list[str]:
        """Stable interface alias for clients that call owned Gu an inventory."""

        return self.owned_gu

    @property
    def current_phase(self) -> str:
        return self.phase

    def record(self, message: str) -> None:
        self.log.append(f"Day {self.day}: {message}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PlayerCharacter":
        return cls(
            name=str(data.get("name", "未央")),
            origin=_normalise_origin(str(data.get("origin", "散修"))),
            aptitude=str(data.get("aptitude", "乙等")),
            rank=str(data.get("rank", "一转初阶")),
            primeval_essence=_as_int(data.get("primeval_essence"), 30),
            health=max(0, min(100, _as_int(data.get("health"), 100))),
            owned_gu=[
                str(item)
                for item in data.get(
                    "owned_gu", data.get("gu_inventory", ["月光蛊"])
                )
            ],
            location=str(data.get("location", "村庄")),
            yuan_stones=_as_int(data.get("yuan_stones", data.get("currency")), 20),
            inventory={
                str(k): _as_int(v)
                for k, v in dict(data.get("inventory", {})).items()
            }
            or {"食物": 5},
            day=_as_int(data.get("day"), 1),
            action_points=max(0, min(3, _as_int(data.get("action_points"), 3))),
            phase=str(data.get("phase", "上午")),
            cultivation_progress=_as_int(data.get("cultivation_progress"), 0),
            discovered_locations=[
                str(item) for item in data.get("discovered_locations", ["村庄"])
            ],
            information=[str(item) for item in data.get("information", [])],
            log=[str(item) for item in data.get("log", [])],
            id=str(data.get("id", data.get("character_id", "player-1"))),
        )


# Backward-compatible name used by the original CLI prototype.
PlayerGuMaster = PlayerCharacter


def create_player(
    name: str = "未央", origin: str = "散修", *, seed: int | None = None
) -> PlayerCharacter:
    return PlayerCharacter.create(name, origin, seed=seed)


def _action_name(action: str) -> str:
    aliases = {
        "1": "cultivate",
        "修炼": "cultivate",
        "cultivate": "cultivate",
        "2": "explore",
        "探索": "explore",
        "explore": "explore",
        "3": "gather",
        "采集": "gather",
        "gather": "gather",
        "4": "trade",
        "交易": "trade",
        "trade": "trade",
        "5": "status",
        "状态": "status",
        "status": "status",
        "6": "rest",
        "休息": "rest",
        "结束": "rest",
        "rest": "rest",
    }
    value = str(action).strip()
    return aliases.get(value, aliases.get(value.casefold(), value.casefold()))


def _spend_action(player: PlayerCharacter) -> None:
    if player.action_points <= 0:
        raise ValueError("今日行动次数已耗尽，请结束一天。")
    player.action_points -= 1
    consumed = 3 - player.action_points
    player.phase = PHASES[min(2, consumed)]


def world_tick(player: PlayerCharacter, world: WorldState) -> None:
    """Finish the current day and reset the player's three action points."""

    world.tick(player)
    player.inventory["食物"] = max(0, player.inventory.get("食物", 0) - 1)
    if player.inventory.get("食物", 0) == 0:
        player.health = max(1, player.health - 1)
        player.record("缺少食物，健康-1。")


def _queue_action_event(player: PlayerCharacter, world: WorldState) -> WorldEvent | None:
    event = world._generate_event(player.location)
    if event is not None:
        world.queue_event(event)
    return event


def apply_action(player: PlayerCharacter, world: WorldState, action: str) -> str:
    """Apply one action and return a concise human-readable result."""

    action_name = _action_name(action)
    if action_name == "status":
        return (
            f"地点:{player.location} 真元:{player.primeval_essence} "
            f"元石:{player.yuan_stones} 危险:{world.danger_level} "
            f"行动点:{player.action_points}"
        )
    if action_name not in {"cultivate", "explore", "gather", "trade", "rest"}:
        return "未知行动。"
    if player.action_points <= 0:
        return "今日行动次数已耗尽，请结束一天。"

    _spend_action(player)
    if action_name == "cultivate":
        old = player.primeval_essence
        maximum = 100 if player.aptitude == "乙等" else 120
        player.primeval_essence = min(maximum, old + 5)
        player.cultivation_progress += 5
        result = f"静修，真元+{player.primeval_essence - old}，修为进度+5。"

    elif action_name == "explore":
        neighbors = tuple(
            LOCATIONS.get(player.location, {}).get("neighbors", ("村庄",))
        )
        if neighbors:
            destination = neighbors[world._roll("explore", 0, len(neighbors) - 1)]
            player.location = destination
            if destination not in player.discovered_locations:
                player.discovered_locations.append(destination)
        event = _queue_action_event(player, world)
        if event is not None:
            result = f"探索{player.location}，触发事件：{event.title}。"
        else:
            result = f"探索{player.location}，暂未发现异常。"

    elif action_name == "gather":
        resource = str(LOCATIONS.get(player.location, {}).get("resource", "月兰草"))
        if resource in {"交易", "生活补给"}:
            resource = "食物"
        available = world.resources.get(resource, 0)
        if available > 0:
            world.resources[resource] = available - 1
            player.inventory[resource] = player.inventory.get(resource, 0) + 1
            result = f"采集{resource}成功。"
        else:
            result = f"附近{resource}资源不足。"

    elif action_name == "trade":
        player.location = "坊市"
        traded_resource = next(
            (
                key
                for key in ("兽材", "月兰草", "未知蛊材")
                if player.inventory.get(key, 0) > 0
            ),
            None,
        )
        if traded_resource is not None:
            player.inventory[traded_resource] -= 1
            player.yuan_stones += 3
            result = f"在坊市出售{traded_resource}，获得3元石并听到商路消息。"
        elif player.yuan_stones >= 2:
            player.yuan_stones -= 2
            player.inventory["食物"] = player.inventory.get("食物", 0) + 1
            result = "在坊市购买食物，获得商路消息。"
        else:
            result = "来到坊市，但手头拮据，暂未成交。"
        player.information.append("坊市商路消息")

    else:  # rest
        player.action_points = 0
        result = "结束今日行动，进入下一天。"
        player.record(result)
        world_tick(player, world)
        return result

    player.record(result)
    return result


def resolve_pending_event(
    world: WorldState, player: PlayerCharacter, choice: str
) -> str:
    """Resolve the oldest queued dynamic event and apply its effects."""

    event = world.pop_event()
    if event is None:
        return "当前没有待处理事件。"
    result = resolve_event(event, str(choice))
    EventResolver().apply(result, player=player, world=world)
    player.health = max(0, min(100, player.health))
    world.danger_level = max(0, min(100, world.danger_level))
    if result.description:
        if result.description.startswith("获得附近区域情报"):
            player.information.append(result.description)
        world.record(result.description)
        player.record(result.description)
    return result.description


@dataclass
class PlayableGame:
    """Facade for a complete player/world loop and portable save payload."""

    player: PlayerCharacter
    world: WorldState

    @classmethod
    def new(
        cls,
        seed: int = 20260925,
        name: str = "未央",
        origin: str = "散修",
    ) -> "PlayableGame":
        return cls(
            PlayerCharacter.create(name, origin, seed=seed), WorldState(seed=seed)
        )

    create = new

    @property
    def day(self) -> int:
        return self.world.day

    @property
    def events(self) -> list[str]:
        return self.world.events

    def perform_action(self, action: str) -> str:
        return apply_action(self.player, self.world, action)

    action = perform_action

    def resolve_event(self, choice: str) -> str:
        return resolve_pending_event(self.world, self.player, choice)

    def end_day(self) -> None:
        self.player.action_points = 0
        world_tick(self.player, self.world)

    advance_day = end_day
    tick = end_day

    def run_day(self, actions: Iterable[str] | None = None) -> list[str]:
        chosen = (
            list(actions)
            if actions is not None
            else ["cultivate", "explore", "gather"]
        )
        results: list[str] = []
        for action in chosen:
            if self.player.action_points <= 0:
                break
            results.append(self.perform_action(action))
        if self.world.day == self.player.day:
            self.end_day()
        return results

    def run_days(self, days: int = 30) -> "PlayableGame":
        if not isinstance(days, int) or isinstance(days, bool) or days < 0:
            raise ValueError("days must be a non-negative integer")
        for _ in range(days):
            self.run_day()
            if self.world.event_queue:
                options = self.world.event_queue[0].get("options", [])
                if options:
                    safe_choice = "避开" if "避开" in options else options[-1]
                    self.resolve_event(str(safe_choice))
        return self

    def summary(self) -> dict[str, Any]:
        return {
            "day": self.world.day,
            "player": self.player.to_dict(),
            "world": self.world.to_dict(),
            "history": list(self.world.history),
            "events": list(self.world.events),
        }

    def to_dict(self) -> dict[str, Any]:
        return {"version": 2, "player": self.player.to_dict(), "world": self.world.to_dict()}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PlayableGame":
        if "player" not in data or "world" not in data:
            raise ValueError("playable save requires player and world")
        return cls(
            PlayerCharacter.from_dict(dict(data["player"])),
            WorldState.from_dict(dict(data["world"])),
        )

    def save(self, path: str | Path) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return str(target)

    @classmethod
    def load(cls, path: str | Path) -> "PlayableGame":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


def run_playable(
    seed: int = 20260925,
    days: int = 30,
    name: str = "未央",
    origin: str = "散修",
    *,
    actions: Iterable[Iterable[str]] | None = None,
    interactive: bool = False,
) -> dict[str, Any]:
    """Run the first playable demo and return a JSON-ready summary."""

    game = PlayableGame.new(seed=seed, name=name, origin=origin)
    if interactive:
        for _ in range(days):
            while game.player.action_points > 0:
                prompt = (
                    f"Day {game.day} {game.player.phase} "
                    f"AP={game.player.action_points} [1修炼 2探索 3采集 4交易 6休息]："
                )
                choice = input(prompt).strip()
                print(game.perform_action(choice))
            if game.world.event_queue:
                print("待处理事件：", game.world.events[0])
        return game.summary()

    action_days = list(actions) if actions is not None else None
    for index in range(days):
        day_actions = (
            action_days[index]
            if action_days is not None and index < len(action_days)
            else None
        )
        game.run_day(day_actions)
        if game.world.event_queue:
            options = game.world.event_queue[0].get("options", [])
            if options:
                safe_choice = "避开" if "避开" in options else options[-1]
                game.resolve_event(str(safe_choice))
    return {
        "phase": "V0.1_PLAYABLE",
        "seed": seed,
        "days_requested": days,
        "day": game.day,
        "player": game.player.to_dict(),
        "world": game.world.to_dict(),
        "history": list(game.world.history),
        "event_count": sum(
            "发生事件:" in entry for entry in game.world.history
        ),
    }


__all__ = [
    "LOCATIONS",
    "PHASES",
    "WorldState",
    "PlayerCharacter",
    "PlayerGuMaster",
    "PlayableGame",
    "create_player",
    "world_tick",
    "apply_action",
    "resolve_pending_event",
    "run_playable",
]
