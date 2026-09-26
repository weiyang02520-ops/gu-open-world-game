"""V0.1 save/load foundation.

Provides JSON serialization for playable layer state.
Future versions can extend this into slots, cloud saves and replay history.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path


SAVE_VERSION = 1


def save_game(player, world, path: str = "save.json") -> str:
    """Save player and world state into a portable JSON file."""
    data = {
        "version": SAVE_VERSION,
        "player": asdict(player),
        "world": asdict(world),
    }

    target = Path(path)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(target)


def load_game(path: str = "save.json") -> dict:
    """Load a previously saved state payload."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if data.get("version") != SAVE_VERSION:
        raise ValueError("Unsupported save version")

    return data
