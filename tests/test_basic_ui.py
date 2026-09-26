"""Acceptance tests for the V0.1.2 Phase 1 UI boundary.

The tests intentionally exercise only :class:`ui.controller.GameController`.
The controller is the adapter between a future web/desktop client and the
authoritative ``gu_game.playable`` loop; a UI test must not reach into the
player or world objects and mutate them directly.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import threading
from typing import Any
from urllib.request import Request, urlopen

from ui.controller import GameController


def _new_controller() -> GameController:
    """Use the documented factory while tolerating ``new`` as a compatibility alias."""

    factory = getattr(GameController, "create", None) or getattr(GameController, "new")
    return factory(name="未央", origin="散修", seed=20260926)


def _state(controller: GameController) -> dict[str, Any]:
    """Read a JSON-safe state snapshot through the public API."""

    reader = getattr(controller, "state", None) or getattr(controller, "get_state")
    snapshot = reader()
    assert isinstance(snapshot, dict)
    return snapshot


def test_controller_startup_exposes_player_world_and_action_state() -> None:
    controller = _new_controller()
    snapshot = _state(controller)

    assert snapshot["day"] == 1
    assert snapshot["player"]["name"] == "未央"
    assert snapshot["player"]["origin"] == "散修"
    assert snapshot["player"]["action_points"] == 3
    assert "world" in snapshot

    # ``state`` is a snapshot boundary. Mutating a returned mapping must not
    # alter the authoritative simulation held by the controller.
    snapshot["player"]["name"] = "UI临时修改"
    assert _state(controller)["player"]["name"] == "未央"


def test_action_button_routes_to_core_and_returns_updated_state() -> None:
    controller = _new_controller()
    before = _state(controller)

    response = controller.action("cultivate")
    assert isinstance(response, dict)
    assert isinstance(response.get("result"), str)
    after = response["state"]
    assert after["player"]["action_points"] == before["player"]["action_points"] - 1
    assert after["player"]["primeval_essence"] > before["player"]["primeval_essence"]


def test_day_advance_and_optional_event_resolution_use_controller_api() -> None:
    controller = _new_controller()
    response = controller.end_day()
    assert response["state"]["day"] == 2
    assert response["state"]["player"]["action_points"] == 3

    # Event resolution is conditional: a world tick is allowed to produce no
    # pending event. When one exists, resolve it through the controller rather
    # than touching ``WorldState.event_queue`` from a UI test/client.
    controller.action("explore")
    pending = _state(controller).get("pending_event")
    if pending:
        options = pending.get("options", [])
        assert options
        choice = "避开" if "避开" in options else options[0]
        event_response = controller.resolve_event(choice)
        assert isinstance(event_response["result"], str)
        assert event_response["state"].get("pending_event") in (None, {})


def test_save_load_restores_the_ui_state_boundary(tmp_path: Path) -> None:
    controller = _new_controller()
    controller.action("gather")
    controller.end_day()
    expected = _state(controller)

    save_path = tmp_path / "ui-slot.json"
    saved = controller.save(save_path)
    assert Path(saved) == save_path
    assert save_path.exists()

    resumed = GameController.load(save_path)
    assert _state(resumed) == expected

    # A resumed controller remains playable and keeps the same public state
    # shape, which is the basis for a future web refresh/render cycle.
    resumed_response = resumed.action("cultivate")
    assert resumed_response["state"]["day"] == expected["day"]
    assert resumed_response["state"]["player"]["action_points"] == 2


def test_ui_app_exposes_a_startup_entrypoint() -> None:
    """The client adapter must be importable without starting a blocking server."""

    app = importlib.import_module("ui.app")
    entrypoints = ("create_app", "create_server", "run_server", "main")
    assert any(callable(getattr(app, name, None)) for name in entrypoints)


def test_ui_http_server_serves_state_and_action_api() -> None:
    """Exercise the dependency-free local transport without a real browser."""

    app = importlib.import_module("ui.app")
    create_server = getattr(app, "create_server", None)
    if create_server is None:
        # The controller contract remains useful for a desktop-only adapter;
        # the startup test above still records that an entrypoint exists.
        return

    server = create_server(host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(f"{base}/api/state", timeout=2) as response:
            initial = json.loads(response.read().decode("utf-8"))
        assert initial["ok"] is True
        assert initial["day"] == 1

        payload = json.dumps({"action": "cultivate"}).encode("utf-8")
        request = Request(
            f"{base}/api/action",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2) as response:
            acted = json.loads(response.read().decode("utf-8"))
        assert acted["ok"] is True
        assert acted["state"]["action_points"] == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_ui_http_server_serves_phase1_page_assets() -> None:
    app = importlib.import_module("ui.app")
    server = app.create_server(host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(f"{base}/", timeout=2) as response:
            page = response.read().decode("utf-8")
        with urlopen(f"{base}/static/style.css", timeout=2) as response:
            style = response.read().decode("utf-8")
        with urlopen(f"{base}/static/app.js", timeout=2) as response:
            script = response.read().decode("utf-8")
        assert "创建蛊师" in page and "行动" in page
        assert ".layout" in style and "action-grid" in style
        assert "/api/action" in script and "/api/event/resolve" in script
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
