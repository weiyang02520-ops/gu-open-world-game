"""Deterministic autonomous NPC simulation for the V0.1 playable layer."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
from typing import Any, Iterable, Mapping


LOCATIONS = ("村庄", "荒林", "坊市", "山洞")


def _stable_index(*parts: object, modulo: int) -> int:
    key = "\x1f".join(str(item) for item in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big") % modulo


def _stable_id(name: str, role: str, location: str) -> str:
    # Keep common names readable, while hashing non-ASCII names so ids remain
    # stable and collision-resistant without introducing random UUID state.
    ascii_name = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not ascii_name:
        ascii_name = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    role_key = re.sub(r"[^a-z0-9]+", "-", role.lower()).strip("-") or "npc"
    location_key = hashlib.sha1(location.encode("utf-8")).hexdigest()[:6]
    return f"npc-{ascii_name}-{role_key}-{location_key}"


@dataclass
class NPCState:
    """A saveable NPC whose routine advances when the player is idle.

    The first seven fields preserve the original prototype constructor.  Both
    ``npc_id`` and ``id`` are accepted for integrations that use either naming
    convention; they are synchronized to the same stable identifier.
    """

    name: str
    role: str
    location: str
    goal: str
    status: str = "idle"
    inventory: dict[str, int] = field(default_factory=dict)
    relationship: dict[str, int] = field(default_factory=dict)
    wealth: int = 0
    memory: list[str] = field(default_factory=list)
    npc_id: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        supplied = self.npc_id or self.id
        stable = supplied or _stable_id(self.name, self.role, self.location)
        self.npc_id = str(stable)
        self.id = self.npc_id
        self.name = str(self.name)
        self.role = str(self.role)
        self.location = str(self.location)
        self.goal = str(self.goal)
        self.status = str(self.status)
        self.wealth = max(0, int(self.wealth))
        self.inventory = {str(key): int(value) for key, value in self.inventory.items()}
        self.relationship = {str(key): int(value) for key, value in self.relationship.items()}
        self.memory = [str(item) for item in self.memory]

    @property
    def stable_id(self) -> str:
        return self.npc_id

    def tick(self, day: int = 1, rng: Any = None, world: Any = None) -> str:
        """Advance this NPC one world tick and return a human-readable action.

        No process-global randomness is used.  A supplied deterministic RNG is
        accepted for future integration, but routine selection remains stable
        for the same NPC/day even when a caller omits it.
        """

        day = max(1, int(day))
        goal = self.goal.lower()
        action = "resting"

        if goal in {"collect", "gather", "采集"} or self.role in {"villager", "村民"}:
            action = "collecting"
            self.inventory["resource"] = self.inventory.get("resource", 0) + 1
            self.status = action
            self._remember(day, "collecting resource")
            self._record_world(world, f"{self.name}采集了资源")
        elif goal in {"trade", "merchant", "交易"} or self.role in {"merchant", "商人"}:
            if day % 2:
                action = "trading"
                self.wealth += 1
                self.inventory["trade_goods"] = self.inventory.get("trade_goods", 0) + 1
            else:
                action = "moving"
                self.location = LOCATIONS[_stable_index(self.npc_id, day, modulo=len(LOCATIONS))]
            self.status = action
            self._remember(day, action)
            self._record_world(world, f"{self.name}{action}")
        elif goal in {"patrol", "guard", "investigate", "巡逻", "调查"} or self.role in {"faction_member", "patroller", "巡山弟子"}:
            action = "patrolling" if day % 3 else "investigating"
            self.status = action
            self._remember(day, action)
            self._record_world(world, f"{self.name}{action}")
        elif goal in {"rest", "休息"}:
            action = "resting"
            self.status = action
            self._remember(day, action)
            self._record_world(world, f"{self.name}休息")
        else:
            # A custom goal still makes progress in its own memory rather than
            # becoming a no-op.  This is useful for future faction missions.
            action = f"pursuing:{self.goal}"
            self.status = action
            self._remember(day, action)
            self._record_world(world, f"{self.name}执行目标:{self.goal}")
        return f"{self.name} -> {self.status}"

    def _remember(self, day: int, action: str) -> None:
        self.memory.append(f"day-{day}:{action}")

    @staticmethod
    def _record_world(world: Any, message: str) -> None:
        if world is None:
            return
        if isinstance(world, dict):
            world.setdefault("history", []).append(message)
        elif hasattr(world, "record") and callable(world.record):
            world.record(message)
        elif hasattr(world, "history") and isinstance(world.history, list):
            world.history.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "npc_id": self.npc_id,
            "id": self.npc_id,
            "name": self.name,
            "role": self.role,
            "location": self.location,
            "goal": self.goal,
            "status": self.status,
            "wealth": self.wealth,
            "inventory": dict(self.inventory),
            "relationship": dict(self.relationship),
            "memory": list(self.memory),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "NPCState":
        return cls(
            name=str(data.get("name", "无名NPC")),
            role=str(data.get("role", "villager")),
            location=str(data.get("location", "村庄")),
            goal=str(data.get("goal", "rest")),
            status=str(data.get("status", "idle")),
            inventory={str(key): int(value) for key, value in data.get("inventory", {}).items()},
            relationship={str(key): int(value) for key, value in data.get("relationship", {}).items()},
            wealth=int(data.get("wealth", 0)),
            memory=[str(item) for item in data.get("memory", [])],
            npc_id=str(data.get("npc_id", data.get("id", ""))),
        )

    def clone(self) -> "NPCState":
        return self.from_dict(self.to_dict())


def default_npcs() -> list[NPCState]:
    """Return a fresh starter roster for each new simulation."""

    return [
        NPCState("村民甲", "villager", "村庄", "collect", wealth=5),
        NPCState("坊市商人", "merchant", "坊市", "trade", wealth=20),
        NPCState("巡山弟子", "faction_member", "荒林", "patrol", wealth=10),
    ]


# Kept as a public compatibility constant.  ``run_npc_tick`` clones it when
# no roster is supplied, preventing one demo run from contaminating another.
DEFAULT_NPCS = default_npcs()


def run_npc_tick(
    npcs: Iterable[NPCState] | None = None,
    *,
    day: int = 1,
    rng: Any = None,
    world: Any = None,
) -> list[str]:
    """Advance every NPC and return the existing list-of-lines view."""

    roster = list(npcs) if npcs is not None else [npc.clone() for npc in DEFAULT_NPCS]
    return [npc.tick(day=day, rng=rng, world=world) for npc in roster]


@dataclass
class NPCSimulation:
    """Small durable roster wrapper for the playable world loop."""

    npcs: list[NPCState] = field(default_factory=default_npcs)
    day: int = 1

    def tick(self, *, world: Any = None, rng: Any = None) -> list[str]:
        self.day += 1
        return [npc.tick(day=self.day, rng=rng, world=world) for npc in self.npcs]

    def to_dict(self) -> dict[str, Any]:
        return {"day": self.day, "npcs": [npc.to_dict() for npc in self.npcs]}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "NPCSimulation":
        return cls(
            npcs=[NPCState.from_dict(item) for item in data.get("npcs", [])],
            day=int(data.get("day", 1)),
        )


__all__ = ["NPCState", "NPCSimulation", "DEFAULT_NPCS", "default_npcs", "run_npc_tick"]
