"""Seeded random source with JSON-safe state persistence."""

from __future__ import annotations

import random
from typing import Any, Sequence, TypeVar


T = TypeVar("T")


def _to_json_safe(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_to_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_to_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_json_safe(item) for key, item in value.items()}
    return value


def _from_json_safe(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_from_json_safe(item) for item in value)
    if isinstance(value, dict):
        return {key: _from_json_safe(item) for key, item in value.items()}
    return value


class DeterministicRNG:
    """A dedicated RNG that never touches Python's global random state."""

    def __init__(self, seed: int) -> None:
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError("seed must be an integer")
        self.seed = seed
        self._random = random.Random(seed)

    def random(self) -> float:
        return self._random.random()

    def randint(self, start: int, end: int) -> int:
        return self._random.randint(start, end)

    def choice(self, values: Sequence[T]) -> T:
        if not values:
            raise IndexError("cannot choose from an empty sequence")
        return self._random.choice(values)

    def get_state(self) -> list[Any]:
        return _to_json_safe(self._random.getstate())

    def set_state(self, state: list[Any]) -> None:
        self._random.setstate(_from_json_safe(state))

    def to_dict(self) -> dict[str, Any]:
        return {"seed": self.seed, "state": self.get_state()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeterministicRNG":
        rng = cls(int(data["seed"]))
        rng.set_state(data["state"])
        return rng
