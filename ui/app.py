"""Dependency-free Phase 1 Web UI transport.

The browser talks to :class:`ui.controller.GameController`; it never receives
or mutates the authoritative PlayableGame objects.  This module contains only
HTTP/static-file plumbing and can later be replaced by another transport.
"""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from typing import Any, Mapping
from urllib.parse import urlparse

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:  # Works both as ``python -m ui.app`` and ``python ui/app.py``.
    from .controller import GameController
except ImportError:  # pragma: no cover - direct script convenience
    from ui.controller import GameController

STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


class UIRequestHandler(BaseHTTPRequestHandler):
    """Serve the Phase 1 page and JSON command/query endpoints."""

    controller: GameController

    def log_message(self, fmt: str, *args: Any) -> None:  # pragma: no cover
        sys.stderr.write("[gu-ui] " + fmt % args + "\n")

    def _send_bytes(self, payload: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, value: Mapping[str, Any], status: int = 200) -> None:
        self._send_bytes(_json_bytes(value), "application/json; charset=utf-8", status)

    def _error(self, message: str, status: int = 400) -> None:
        self._send_json({"ok": False, "error": str(message)}, status)

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length 无效") from exc
        raw = self.rfile.read(max(0, length))
        if not raw:
            return {}
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("请求体必须是 JSON 对象")
        return dict(value)

    def _serve_file(self, path: Path, content_type: str) -> None:
        try:
            payload = path.read_bytes()
        except OSError:
            self._error("资源不存在", HTTPStatus.NOT_FOUND)
            return
        self._send_bytes(payload, content_type)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/":
            self._serve_file(TEMPLATE_DIR / "index.html", "text/html; charset=utf-8")
        elif path == "/static/style.css":
            self._serve_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
        elif path == "/static/app.js":
            self._serve_file(STATIC_DIR / "app.js", "text/javascript; charset=utf-8")
        elif path == "/api/state":
            self._send_json(self.controller.state())
        else:
            self._error("资源不存在", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            body = self._read_json()
            if path in {"/api/create", "/api/player/create"}:
                state = self.controller.create_player(
                    name=str(body.get("name", "未央")),
                    origin=str(body.get("origin", "散修")),
                    seed=body.get("seed"),
                )
                response = {"ok": True, "state": state}
            elif path in {"/api/action", "/api/perform-action"}:
                action = body.get("action", body.get("id", ""))
                if not str(action).strip():
                    raise ValueError("缺少 action")
                response = self.controller.action(str(action))
            elif path in {"/api/end-day", "/api/tick"}:
                response = self.controller.end_day()
            elif path in {"/api/event/resolve", "/api/resolve-event"}:
                choice = body.get("choice", body.get("option", ""))
                if not str(choice).strip():
                    raise ValueError("缺少 choice")
                response = self.controller.resolve_event(str(choice))
            elif path == "/api/save":
                response = {"ok": True, "path": self.controller.save(body.get("path")), "state": self.controller.state()}
            elif path == "/api/load":
                response = {"ok": True, "state": self.controller.load_game(body.get("path"))}
            else:
                self._error("接口不存在", HTTPStatus.NOT_FOUND)
                return
        except FileNotFoundError as exc:
            self._error(str(exc), HTTPStatus.NOT_FOUND)
            return
        except (TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
            self._error(str(exc), HTTPStatus.BAD_REQUEST)
            return
        self._send_json(response)


def create_server(host: str = "127.0.0.1", port: int = 8000, *, controller: GameController | None = None) -> ThreadingHTTPServer:
    """Create a testable server without starting a blocking loop."""

    class BoundHandler(UIRequestHandler):
        pass

    # A server-created session starts at the character-creation screen. The
    # controller still holds a deterministic default state until /api/create.
    BoundHandler.controller = controller or GameController()
    return ThreadingHTTPServer((host, int(port)), BoundHandler)


create_app = create_server


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_server(host, port)
    print(f"GU Game UI running at http://{host}:{server.server_port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nUI stopped.")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GU Game V0.1.2 Phase 1 Web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    run_server(args.host, args.port)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["GameController", "UIRequestHandler", "create_server", "create_app", "run_server", "main"]
