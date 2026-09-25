"""Deterministic world time.

The simulation stores elapsed seconds as an integer.  Rendering and future
systems can choose their own resolution without introducing wall-clock time
or floating-point drift into the authoritative state.
"""

from __future__ import annotations

from dataclasses import dataclass


SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR


@dataclass
class WorldClock:
    """Authoritative elapsed time for one simulation."""

    elapsed_seconds: int = 0
    tick_seconds: int = SECONDS_PER_MINUTE

    def __post_init__(self) -> None:
        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative")
        if self.tick_seconds <= 0:
            raise ValueError("tick_seconds must be positive")

    @property
    def day_number(self) -> int:
        """Return a one-based in-game day number."""

        return self.elapsed_seconds // SECONDS_PER_DAY + 1

    @property
    def hour_of_day(self) -> int:
        return (self.elapsed_seconds % SECONDS_PER_DAY) // SECONDS_PER_HOUR

    def advance(self, seconds: int) -> int:
        """Advance by a non-negative integer number of seconds."""

        if not isinstance(seconds, int) or isinstance(seconds, bool):
            raise TypeError("seconds must be an integer")
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        self.elapsed_seconds += seconds
        return self.elapsed_seconds

    def advance_ticks(self, ticks: int = 1) -> int:
        """Advance by whole simulation ticks."""

        if not isinstance(ticks, int) or isinstance(ticks, bool):
            raise TypeError("ticks must be an integer")
        if ticks < 0:
            raise ValueError("ticks cannot be negative")
        return self.advance(ticks * self.tick_seconds)

    def to_dict(self) -> dict[str, int]:
        return {
            "elapsed_seconds": self.elapsed_seconds,
            "tick_seconds": self.tick_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> "WorldClock":
        return cls(
            elapsed_seconds=int(data["elapsed_seconds"]),
            tick_seconds=int(data.get("tick_seconds", SECONDS_PER_MINUTE)),
        )
