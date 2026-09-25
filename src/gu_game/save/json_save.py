"""Versioned JSON persistence for the M0 world state."""

from __future__ import annotations

import json
from pathlib import Path

from ..core.state import WorldState


def save_world(state: WorldState, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(state.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def load_world(path: str | Path) -> WorldState:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("world save must contain a JSON object")
    return WorldState.from_dict(data)
