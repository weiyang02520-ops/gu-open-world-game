# V0.1 Playable Layer

The first playable layer is a deterministic, headless vertical slice.  It is
deliberately independent of a rendering or network client: a future client
can read the same player/world state and call the same action interface.

The package keeps explicit `network/`, `server/`, `realtime/`, and
`multiplayer/` namespaces as integration boundaries. They contain no gameplay
authority in V0.1; all rules remain in the deterministic layer.

## Start the loop

From a checkout:

```powershell
python main.py --scenario play
```

The installed package exposes the identical launcher:

```powershell
python -m gu_game --scenario play
```

The `play` scenario is a terminal adapter.  Rules remain in
`gu_game.playable`; no UI input is part of the authoritative state.

## V0.1.2 Phase 1 basic UI boundary

Phase 1 adds a thin client adapter under `ui/`.  It is intentionally a
presentation boundary, not a second game engine:

```text
Web or desktop view
        |
        v
ui.controller.GameController
        |
        v
gu_game.playable -> WorldState / PlayerCharacter / EventResolver / Save
```

`GameController.state()` returns a JSON-safe snapshot.  UI code submits an
action through `action(name)`, advances the world with `end_day()`, resolves a
pending event with `resolve_event(choice)`, and uses `save(path)` /
`GameController.load(path)` for persistence.  A state snapshot is copied at
the boundary, so rendering code cannot mutate the authoritative player or
world objects directly.

The lightweight web adapter can be started with:

```powershell
python -m ui.app
python main.py --scenario ui
```

The local transport exposes read-only state and command endpoints used by the
Phase 1 page:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/state` | Read the current UI snapshot |
| `POST` | `/api/create` | Create a player (`name`, optional `origin`) |
| `POST` | `/api/action` | Submit one action (`action`) |
| `POST` | `/api/end-day` | Run the world tick |
| `POST` | `/api/event/resolve` | Resolve a pending event (`choice`) |
| `POST` | `/api/save` / `/api/load` | Save or restore a local slot |

The transport is intentionally local and dependency-free.  It is suitable for
Phase 1 smoke tests and can later be replaced by a different server or client
without changing the controller contract.

The same controller is available to an embedding client without starting a
server:

```python
from ui.controller import GameController

game = GameController.create(name="未央", origin="散修", seed=20260926)
view_model = game.state()
view_model = game.action("cultivate")["state"]
game.end_day()
game.save("savegames/ui-slot.json")
resumed = GameController.load("savegames/ui-slot.json")
```

The Phase 1 surface covers the player status bar, current location, world
summary, action buttons, event panel, and history log.  The node map, Gu cards,
NPC cards, and visual assets remain later UI phases; no 3D engine or generated
insect imagery is required for this boundary.

## Non-interactive API

The small public API is suitable for smoke tests, a future UI, or a network
adapter:

```python
from gu_game.playable import PlayableGame, create_player

player = create_player("未央", origin="散修", seed=20260926)
game = PlayableGame.new(20260926, name="未央", origin="散修")
game.perform_action("1")  # cultivate; one of three daily action points
game.end_day()             # world tick, NPC tick, events, next day
game.run_days(30)          # deterministic headless demo
```

`PlayerCharacter` is the canonical player model.  `PlayerGuMaster` remains a
compatibility alias for earlier saves and callers.  A new player starts as a
Rank 1 Gu Master with 30 primeval essence, 20 yuan stones, and the `月光蛊`
instance.  The origin (`散修` or `家族弟子`) is carried as player state and can
be consumed by later faction systems.

Supported action families in the current adapter are cultivation, exploration,
gathering, travel/trade, status inspection, and ending the day.  Every action
spends one action point except the explicit end-day transition.  A world tick
advances the in-game day, updates resources/NPC status, and records events in
history.  It does not use wall-clock time or Python's process-global random
source as an authority.

## Save / Load / Resume

The compatibility helper keeps the original two-object signature:

```python
from gu_game.save_load import load_playable_game, save_game

save_game(game.player, game.world, "savegames/slot-1.json")
resumed = load_playable_game("savegames/slot-1.json")
resumed.run_days(1)
```

`PlayableGame.save(path)` and `PlayableGame.load(path)` may be used when the
wrapper supplies those convenience methods.  `save_game` writes a versioned
JSON object containing player and world state; parent directories are created
automatically.  `load_game` validates and returns the payload for migration or
inspection, while `load_playable_game` reconstructs a runnable wrapper (or the
legacy `(player, world)` pair when no wrapper is available).  `resume_game` is
an alias for the latter.

The file contains only gameplay state.  It has no rendering/UI state and no
wall-clock timestamp.  The same seed plus the saved state therefore gives a
reproducible continuation and remains compatible with the deterministic core
save boundary in `gu_game.save`.

## Verification

The dedicated playable acceptance tests cover:

- player creation and starting inventory;
- action-point consumption and reset;
- world tick/NPC changes when the player does nothing;
- JSON save/load/resume and continued play;
- a 30-day headless run.

Run them with:

```powershell
pytest -q tests/test_playable_layer.py
```

The complete regression suite remains the source of truth for M1–M8:

```powershell
pytest -q
```

The UI boundary acceptance tests are also runnable on their own:

```powershell
pytest -q tests/test_basic_ui.py
```
