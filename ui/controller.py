"""UI-facing controller for the deterministic playable game.

The browser or desktop layer should use :class:`GameController` as its only
gameplay boundary.  It owns a :class:`~gu_game.playable.PlayableGame` and
returns plain JSON-compatible snapshots/results.  A caller never receives the
authoritative player or world objects, so mutating a value returned by
``state()`` cannot mutate the simulation.

This module intentionally contains no rendering code and no gameplay rules.
The controller is an adapter around the existing playable facade; it keeps
UI concerns (stable response envelopes and serializable snapshots) out of
``src/gu_game``.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping

from gu_game.playable import LOCATIONS, PlayableGame


class GameController:
    """Stable command/query boundary for V0.1.2 UI clients.

    ``GameController`` is deliberately small.  The authoritative state lives
    in the wrapped :class:`PlayableGame`; UI code can only query a deep-copied
    state snapshot or submit a command through the methods below.

    Parameters
    ----------
    game:
        An existing playable game, useful for tests and save restoration.
        When omitted a new deterministic game is created from ``seed``.
    seed, name, origin:
        Passed to :meth:`PlayableGame.new` when ``game`` is omitted.
    """

    API_VERSION = 1
    DEFAULT_SAVE_PATH = Path("savegames/ui-slot-1.json")

    def __init__(
        self,
        game: PlayableGame | None = None,
        *,
        seed: int = 20260926,
        name: str = "未央",
        origin: str = "散修",
    ) -> None:
        self._game = game if game is not None else PlayableGame.new(
            seed=seed,
            name=name,
            origin=origin,
        )
        # A transport-created controller starts behind the character-creation
        # screen; the class factory and save restoration represent an active
        # session immediately.
        self.created = game is not None
        self._validate_game(self._game)

    @staticmethod
    def _validate_game(game: Any) -> None:
        """Fail early if an adapter is accidentally given the wrong object."""

        required = ("perform_action", "end_day", "resolve_event", "to_dict")
        missing = [name for name in required if not callable(getattr(game, name, None))]
        if missing:
            joined = ", ".join(missing)
            raise TypeError(f"game must expose the playable facade ({joined} missing)")
        if not hasattr(game, "player") or not hasattr(game, "world"):
            raise TypeError("game must expose player and world state")

    @classmethod
    def create(
        cls,
        name: str = "未央",
        origin: str = "散修",
        *,
        seed: int = 20260926,
    ) -> "GameController":
        """Create a fresh player and enter day one.

        This is the preferred entry point for a UI's character-creation
        screen.  Validation and defaults remain owned by ``PlayableGame``.
        """

        controller = cls(seed=seed, name=name, origin=origin)
        controller.created = True
        return controller

    # ``new`` mirrors the core facade and makes the adapter convenient for
    # callers that use the same factory for headless and UI sessions.
    new = create

    def create_player(
        self,
        name: str,
        origin: str = "散修",
        *,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Restart this controller with a newly created player.

        Long-lived transports (for example an HTTP server) can use this
        method for the character-creation screen without replacing their
        controller instance.  The actual defaults and origin validation stay
        in ``PlayableGame.new``.
        """

        clean_name = str(name or "").strip()
        if not clean_name:
            raise ValueError("角色名不能为空")
        current_seed = int(getattr(self._game.world, "seed", 20260926))
        self._game = PlayableGame.new(
            seed=current_seed if seed is None else int(seed),
            name=clean_name,
            origin=str(origin or "散修").strip(),
        )
        self.created = True
        return self.state()

    @classmethod
    def from_game(cls, game: PlayableGame) -> "GameController":
        """Wrap an already-created playable game without copying authority."""

        return cls(game=game)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "GameController":
        """Load a saved playable session and wrap it for UI access."""

        target = cls.DEFAULT_SAVE_PATH if path is None or not str(path).strip() else path
        return cls(game=PlayableGame.load(target))

    # ``resume`` is an explicit UI-friendly alias for save/load flows.
    resume = load

    def state(self) -> dict[str, Any]:
        """Return a JSON-compatible, detached snapshot for rendering.

        The nested objects are deep-copied.  A UI may freely sort, annotate,
        or otherwise mutate its local snapshot without changing game state.
        ``pending_event`` is the oldest event awaiting a player choice; it is
        ``None`` when the queue is empty.
        """

        player = deepcopy(self._game.player.to_dict())
        world = deepcopy(self._game.world.to_dict())
        event_queue = list(world.get("event_queue", []))
        snapshot: dict[str, Any] = {
            # The transport can return a state snapshot directly from
            # ``GET /api/state``; keeping the success marker here avoids a
            # second wrapper while remaining harmless for desktop callers.
            "ok": True,
            "api_version": self.API_VERSION,
            "created": self.created,
            "day": int(world.get("day", player.get("day", 1))),
            "phase": str(player.get("phase", "上午")),
            "action_points": int(player.get("action_points", 0)),
            "player": player,
            "world": world,
            "pending_event": deepcopy(event_queue[0]) if event_queue else None,
            "pending_events": deepcopy(event_queue),
            "events": deepcopy(world.get("events", [])),
            "history": deepcopy(world.get("history", [])),
            # A UI can render this graph without importing core model classes.
            "locations": deepcopy(LOCATIONS),
        }
        return snapshot

    # Query aliases kept intentionally boring and stable for different UI
    # frameworks (React adapters often call this get_state).
    get_state = state
    snapshot = state

    def _response(self, result: Any = "") -> dict[str, Any]:
        """Build the common command response envelope."""

        if result is None:
            message = ""
        else:
            message = str(result)
        return {
            "ok": True,
            "result": message,
            "message": message,
            "state": self.state(),
        }

    def action(self, action: str) -> dict[str, Any]:
        """Submit one player action through the playable facade."""

        result = self._game.perform_action(str(action))
        return self._response(result)

    perform_action = action
    submit_action = action

    def end_day(self) -> dict[str, Any]:
        """Advance the world by one day and return the new UI snapshot."""

        self._game.end_day()
        return self._response(f"世界推进至第{self._game.day}天。")

    advance_day = end_day
    tick = end_day

    def resolve_event(self, choice: str) -> dict[str, Any]:
        """Resolve the oldest pending event through ``EventResolver``."""

        result = self._game.resolve_event(str(choice))
        return self._response(result)

    choose_event = resolve_event

    def save(self, path: str | Path | None = None) -> str:
        """Persist the authoritative playable state and return its path."""

        target = self.DEFAULT_SAVE_PATH if path is None or not str(path).strip() else path
        return self._game.save(target)

    save_game = save

    def load_into(self, path: str | Path | None = None) -> dict[str, Any]:
        """Replace this controller's session with a save and return its state.

        Most callers should prefer the class method ``GameController.load``;
        this mutating form is useful for a long-lived UI shell that keeps one
        controller object while the user changes save slots.
        """

        target = self.DEFAULT_SAVE_PATH if path is None or not str(path).strip() else path
        restored = PlayableGame.load(target)
        self._validate_game(restored)
        self._game = restored
        self.created = True
        return self.state()

    load_game = load_into

    def pending_event(self) -> dict[str, Any] | None:
        """Return a detached copy of the oldest pending event, if any."""

        event = self.state().get("pending_event")
        return deepcopy(event) if event is not None else None

    def run_days(self, days: int = 1) -> dict[str, Any]:
        """Run deterministic demo days for non-interactive UI smoke tests."""

        self._game.run_days(days)
        return self._response(f"已运行{days}天。")

    def to_dict(self) -> dict[str, Any]:
        """Alias for :meth:`state` used by generic JSON adapters."""

        return self.state()


__all__ = ["GameController"]
