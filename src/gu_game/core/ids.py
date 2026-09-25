"""Stable entity identifiers for deterministic tests and save files."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EntityIdFactory:
    """Generate readable, deterministic IDs within one simulation."""

    prefix: str = "entity"
    _next_number: int = field(default=1, repr=False)

    def __post_init__(self) -> None:
        if not self.prefix or any(char.isspace() for char in self.prefix):
            raise ValueError("prefix must be a non-empty token")
        if self._next_number < 1:
            raise ValueError("_next_number must be positive")

    def next(self, kind: str | None = None) -> str:
        label = kind or self.prefix
        if not label or any(char.isspace() for char in label):
            raise ValueError("kind must be a non-empty token")
        entity_id = f"{label.lower()}-{self._next_number:06d}"
        self._next_number += 1
        return entity_id

    def to_dict(self) -> dict[str, int | str]:
        return {"prefix": self.prefix, "next_number": self._next_number}

    @classmethod
    def from_dict(cls, data: dict[str, int | str]) -> "EntityIdFactory":
        return cls(
            prefix=str(data["prefix"]),
            _next_number=int(data["next_number"]),
        )
