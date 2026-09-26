"""Phase 1 UI adapter contract tests.

These tests assert the boundary rather than a rendering implementation: the
controller delegates to the playable facade, returns detached snapshots, and
round-trips through the existing JSON save format.
"""

from __future__ import annotations

from pathlib import Path

from ui import GameController


def test_controller_creates_json_safe_state_and_does_not_expose_core_objects() -> None:
    controller = GameController.create("未央", origin="散修", seed=1201)

    state = controller.state()
    assert state["player"]["name"] == "未央"
    assert state["player"]["origin"] == "散修"
    assert state["day"] == 1
    assert state["action_points"] == 3
    assert state["locations"]
    assert not hasattr(controller, "player")
    assert not hasattr(controller, "world")

    # The returned snapshot is detached from the authoritative facade.
    state["player"]["name"] = "UI临时名称"
    state["world"]["history"].append("UI临时日志")
    fresh = controller.state()
    assert fresh["player"]["name"] == "未央"
    assert "UI临时日志" not in fresh["world"]["history"]


def test_controller_action_and_end_day_delegate_to_playable_loop() -> None:
    controller = GameController.create(seed=1202)

    action_response = controller.action("cultivate")
    assert action_response["ok"] is True
    assert action_response["state"]["action_points"] == 2
    assert action_response["state"]["player"]["primeval_essence"] == 35

    day_response = controller.end_day()
    assert day_response["ok"] is True
    assert day_response["state"]["day"] == 2
    assert day_response["state"]["action_points"] == 3


def test_controller_save_load_and_event_resolution_round_trip(tmp_path: Path) -> None:
    controller = GameController.create(seed=1203)
    controller.action("explore")
    save_path = tmp_path / "ui" / "slot.json"
    assert controller.save(save_path) == str(save_path)

    resumed = GameController.load(save_path)
    assert resumed.state() == controller.state()
    pending = resumed.pending_event()
    if pending is not None:
        response = resumed.resolve_event(pending["options"][0])
        assert response["ok"] is True

    # The mutating load form supports a long-lived UI shell as well.
    shell = GameController.create(seed=999)
    loaded_state = shell.load_into(save_path)
    assert loaded_state == controller.state()

