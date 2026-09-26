"""Portable persistence helpers for the V0.1 playable layer.

The headless playable prototype has deliberately kept its state as plain
dataclasses.  This module is the small boundary between those objects and a
JSON save file.  It accepts both the original ``PlayerGuMaster``/``WorldState``
objects and the newer ``PlayerCharacter``/``PlayableGame`` names, while leaving
the authoritative rules in :mod:`gu_game.playable`.

``save_game`` retains the original two-object signature.  ``load_game`` keeps
returning the decoded payload for callers that need to inspect or migrate a
save.  ``load_playable_game``/``resume_game`` rebuild a runnable
``PlayableGame`` when that class is available and otherwise return the
reconstructed ``(player, world)`` pair.  No wall-clock value is written to a
save; deterministic game time belongs to the world object.
"""

from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, Mapping, TypeVar


# Version 2 adds type metadata and supports PlayableGame state without
# invalidating the version-1 two-object files produced by the first prototype.
SAVE_VERSION = 2
_SUPPORTED_VERSIONS = {1, SAVE_VERSION}
T = TypeVar("T")


def _json_safe(value: Any) -> Any:
    """Convert a model value into JSON-compatible primitives."""

    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    # Core objects such as WorldState expose an explicit, lossless serializer.
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _json_safe(value.to_dict())
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"cannot serialize {type(value).__name__} to a game save")


def _model_to_dict(value: Any) -> dict[str, Any]:
    """Serialize a model, preferring its explicit ``to_dict`` method."""

    payload = value.to_dict() if hasattr(value, "to_dict") and callable(value.to_dict) else value
    payload = _json_safe(payload)
    if not isinstance(payload, dict):
        raise TypeError(f"playable save models must serialize to an object, got {type(payload).__name__}")
    return payload


def _write_payload(payload: dict[str, Any], path: str | Path) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return str(target)


def save_game(player: Any, world: Any, path: str | Path = "save.json") -> str:
    """Save a player/world pair into a portable JSON file.

    The signature remains compatible with the first playable prototype.  A
    caller may pass either the current ``PlayerCharacter`` and playable
    ``WorldState`` or legacy ``PlayerGuMaster`` objects.  Type hints are for
    diagnostics only; loaders never import arbitrary code named by a save.
    """

    payload = {
        "version": SAVE_VERSION,
        "player_type": type(player).__name__,
        "world_type": type(world).__name__,
        "player": _model_to_dict(player),
        "world": _model_to_dict(world),
    }
    return _write_payload(payload, path)


def _read_payload(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("game save must contain a JSON object")
    version = payload.get("version")
    # Version 1 was the original two-dataclass format.  Missing version is
    # rejected so malformed files cannot silently become fresh games.
    if version not in _SUPPORTED_VERSIONS:
        raise ValueError(f"Unsupported save version: {version!r}")
    for key in ("player", "world"):
        if not isinstance(payload.get(key), dict):
            raise ValueError(f"game save field {key!r} must be an object")
    return payload


def load_game(path: str | Path = "save.json") -> dict[str, Any]:
    """Load and validate a save payload without constructing game objects."""

    return _read_payload(path)


def _construct_model(model_cls: type[T], data: Mapping[str, Any]) -> T:
    """Construct one model using its explicit deserializer when available."""

    from_dict = getattr(model_cls, "from_dict", None)
    if callable(from_dict):
        return from_dict(dict(data))

    # Legacy playable models are ordinary dataclasses.  Filter unknown keys so
    # a newer save can still be opened by an older compatible model; missing
    # fields retain dataclass defaults.
    if is_dataclass(model_cls):
        accepted = {field.name for field in fields(model_cls) if field.init}
        values = {key: value for key, value in data.items() if key in accepted}
        return model_cls(**values)
    try:
        return model_cls(**dict(data))
    except TypeError as exc:
        raise ValueError(f"cannot reconstruct {model_cls.__name__} from save") from exc


def _playable_classes() -> tuple[type[Any], type[Any], type[Any] | None]:
    # Lazy import avoids making the interactive playable implementation a
    # requirement for callers that only use core save/load helpers.
    from . import playable

    player_cls = getattr(playable, "PlayerCharacter", None) or getattr(playable, "PlayerGuMaster", None)
    world_cls = getattr(playable, "WorldState", None)
    game_cls = getattr(playable, "PlayableGame", None)
    if player_cls is None or world_cls is None:
        raise RuntimeError("playable module does not expose PlayerCharacter/WorldState")
    return player_cls, world_cls, game_cls


def load_playable_game(path: str | Path = "save.json") -> Any:
    """Reconstruct a runnable playable game from a save.

    New playable implementations should expose ``PlayableGame.from_state`` or
    ``PlayableGame.from_objects``.  We also support a constructor accepting
    ``player=`` and ``world=``.  If no game wrapper is present, the function
    returns ``(player, world)`` for callers using free functions.
    """

    payload = _read_payload(path)
    player_cls, world_cls, game_cls = _playable_classes()
    player = _construct_model(player_cls, payload["player"])
    world = _construct_model(world_cls, payload["world"])

    if game_cls is None:
        return player, world

    # Prefer explicit class-level restoration hooks.  Save metadata is never
    # treated as an import path or executable code.
    for hook_name in ("from_state", "from_objects"):
        hook = getattr(game_cls, hook_name, None)
        if not callable(hook):
            continue
        for args, kwargs in (((player, world), {}), ((), {"player": player, "world": world})):
            try:
                return hook(*args, **kwargs)
            except TypeError:
                continue

    for args, kwargs in (((player, world), {}), ((), {"player": player, "world": world})):
        try:
            return game_cls(*args, **kwargs)
        except TypeError:
            continue
    raise ValueError(f"cannot reconstruct {game_cls.__name__} from save")


def resume_game(path: str | Path = "save.json") -> Any:
    """Alias for :func:`load_playable_game` used by CLI/front-end callers."""

    return load_playable_game(path)


__all__ = [
    "SAVE_VERSION",
    "load_game",
    "load_playable_game",
    "resume_game",
    "save_game",
]
