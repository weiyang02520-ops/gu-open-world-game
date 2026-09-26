"""V0.1 NPC simulation.

NPCs are intentionally independent from the player. The world can continue
running even when the player does not interact with them.
"""

from dataclasses import dataclass, field


@dataclass
class NPCState:
    name: str
    role: str
    location: str
    goal: str
    status: str = "idle"
    inventory: dict[str, int] = field(default_factory=dict)
    relationship: dict[str, int] = field(default_factory=dict)

    def tick(self) -> str:
        if self.goal == "collect":
            self.status = "collecting"
            self.inventory["resource"] = self.inventory.get("resource", 0) + 1
        elif self.goal == "trade":
            self.status = "trading"
        else:
            self.status = "patrolling"
        return f"{self.name} -> {self.status}"


DEFAULT_NPCS = [
    NPCState("村民甲", "villager", "村庄", "collect"),
    NPCState("坊市商人", "merchant", "坊市", "trade"),
    NPCState("巡山弟子", "faction_member", "荒林", "patrol"),
]


def run_npc_tick(npcs=None):
    npcs = npcs or DEFAULT_NPCS
    return [npc.tick() for npc in npcs]
