"""Acceptance tests for the V0.1 playable headless vertical slice.

These tests exercise the public playable API rather than implementation
details.  They intentionally keep the seed explicit so a Save/Resume run is
reproducible in CI and on another executor.
"""

from __future__ import annotations

from pathlib import Path

from gu_game.playable import PlayableGame, PlayerCharacter, create_player
from gu_game.save_load import load_game, load_playable_game, save_game


def _action(game: PlayableGame, action: str) -> object:
    """Call the public action method used by the current playable wrapper."""

    for name in ("perform_action", "action", "apply_action"):
        method = getattr(game, name, None)
        if callable(method):
            return method(action)
    raise AssertionError("PlayableGame must expose perform_action/action/apply_action")


def _end_day(game: PlayableGame) -> object:
    for name in ("end_day", "world_tick"):
        method = getattr(game, name, None)
        if callable(method):
            return method()
    raise AssertionError("PlayableGame must expose end_day/world_tick")


def test_player_creation_defaults_to_a_playable_gu_master() -> None:
    player = create_player("未央", origin="散修", seed=101)

    assert isinstance(player, PlayerCharacter)
    assert player.name == "未央"
    assert player.origin == "散修"
    assert player.rank.startswith("一转")
    assert player.primeval_essence == 30
    assert player.yuan_stones == 20
    assert "月光蛊" in player.owned_gu
    assert player.location == "村庄"
    assert player.action_points == 3


def test_actions_consume_points_and_world_tick_resets_the_day() -> None:
    game = PlayableGame.new(102, name="未央", origin="家族弟子")
    initial_day = game.world.day
    initial_essence = game.player.primeval_essence

    _action(game, "1")

    assert game.player.action_points == 2
    assert game.player.primeval_essence > initial_essence

    _end_day(game)

    assert game.world.day > initial_day
    assert game.player.day == game.world.day
    assert game.player.action_points == 3


def test_world_tick_moves_npc_and_records_history_without_player_action() -> None:
    game = PlayableGame.new(103)
    before_status = dict(getattr(game.world, "npc_status", {}))

    _end_day(game)
    _end_day(game)

    assert game.world.day >= 3
    assert getattr(game.world, "history", [])
    after_status = getattr(game.world, "npc_status", {})
    assert after_status != before_status or len(game.world.history) >= 2


def test_save_load_resume_preserves_player_world_and_can_continue(tmp_path: Path) -> None:
    game = PlayableGame.new(104)
    _action(game, "3")
    _end_day(game)
    path = tmp_path / "savegames" / "playable.json"

    # The wrapper's save method is preferred when supplied; the two-object
    # helper remains the compatibility path for the initial prototype.
    save_method = getattr(game, "save", None)
    if callable(save_method):
        save_method(path)
    else:
        save_game(game.player, game.world, path)

    payload = load_game(path)
    assert payload["version"] >= 1
    assert payload["player"]["name"] == game.player.name
    assert payload["world"]["day"] == game.world.day

    resumed = load_playable_game(path)
    assert resumed.player.name == game.player.name
    assert resumed.world.day == game.world.day
    _end_day(resumed)
    assert resumed.world.day == game.world.day + 1


def test_thirty_day_demo_runs_without_wall_clock_or_exceptions() -> None:
    game = PlayableGame.new(105)

    run_days = getattr(game, "run_days", None)
    assert callable(run_days), "PlayableGame.run_days is the deterministic demo API"
    run_days(30)

    assert game.world.day >= 30
    assert game.player.day == game.world.day
    assert len(getattr(game.world, "history", [])) >= 29
    assert game.player.health > 0


def test_same_seed_and_pending_event_resume_are_exact(tmp_path: Path) -> None:
    first = PlayableGame.new(1)
    second = PlayableGame.new(1)
    for _ in range(3):
        first.end_day()
        second.end_day()
    assert first.to_dict() == second.to_dict()
    assert first.world.event_queue

    path = tmp_path / "pending" / "event.json"
    first.save(path)
    resumed = load_playable_game(path)
    assert resumed.to_dict() == first.to_dict()
    choice = resumed.world.event_queue[0]["options"][0]
    first.resolve_event(choice)
    resumed.resolve_event(choice)
    assert resumed.to_dict() == first.to_dict()


def test_event_generation_does_not_depend_on_process_global_random() -> None:
    import random

    random.seed(11)
    first = PlayableGame.new(107)
    first.run_days(5)
    random.seed(987654)
    second = PlayableGame.new(107)
    second.run_days(5)
    assert second.to_dict() == first.to_dict()
