from gu_game.core.events import DomainEvent
from gu_game.core.state import WorldState


def _run(seed: int) -> dict:
    state = WorldState.new(seed)
    state.clock.advance_ticks(3)
    event_id = state.entity_ids.next("event")
    event = DomainEvent(
        event_id=event_id,
        event_type="RNG_SAMPLE",
        timestamp=state.clock.elapsed_seconds,
        payload={"roll": state.rng.randint(1, 100), "chance": state.rng.random()},
    )
    state.record_event(event)
    state.entities["player-000001"] = {
        "kind": "CHARACTER",
        "name": "自创蛊师",
        "roll": state.rng.randint(1, 100),
    }
    return state.to_dict()


def test_same_seed_and_inputs_are_reproducible() -> None:
    assert _run(20260925) == _run(20260925)


def test_different_seed_changes_rng_trace() -> None:
    assert _run(20260925) != _run(20260926)
