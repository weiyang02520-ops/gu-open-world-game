from pathlib import Path

from gu_game.core.events import DomainEvent
from gu_game.core.state import WorldState
from gu_game.save import load_world, save_world


def test_save_load_preserves_core_state(tmp_path: Path) -> None:
    state = WorldState.new(77)
    state.clock.advance(3_600)
    state.entities[state.entity_ids.next("character")] = {
        "kind": "CHARACTER",
        "cultivation": {"rank": 1, "minor_stage": "INITIAL"},
    }
    state.record_event(
        DomainEvent(
            event_id=state.entity_ids.next("event"),
            event_type="REST",
            timestamp=state.clock.elapsed_seconds,
            actor_id="character-000001",
        )
    )

    path = save_world(state, tmp_path / "savegames" / "slot-1.json")
    restored = load_world(path)

    assert restored.to_dict() == state.to_dict()


def test_save_load_continues_rng_sequence(tmp_path: Path) -> None:
    state = WorldState.new(9)
    state.rng.random()
    path = save_world(state, tmp_path / "state.json")
    restored = load_world(path)

    assert restored.rng.randint(1, 1_000_000) == state.rng.randint(1, 1_000_000)
