from gu_game.core.clock import WorldClock
from gu_game.core.events import DomainEvent, EventBus, EventVisibility


def test_world_clock_advances_in_ticks_and_reports_day() -> None:
    clock = WorldClock(tick_seconds=30)

    assert clock.day_number == 1
    assert clock.advance_ticks(2) == 60
    assert clock.hour_of_day == 0
    assert clock.advance(24 * 60 * 60) == 86_460
    assert clock.day_number == 2


def test_event_bus_preserves_history_and_dispatches_handlers() -> None:
    bus = EventBus()
    received: list[str] = []
    bus.subscribe("HARVEST", lambda event: received.append(event.event_id))
    event = DomainEvent(
        event_id="event-000001",
        event_type="HARVEST",
        timestamp=120,
        actor_id="character-000001",
        location_id="location-000001",
        payload={"resource": "spirit_grass", "quantity": 2},
        visibility=EventVisibility.OBSERVERS,
    )

    bus.publish(event)
    assert bus.pending_count == 1
    assert bus.dispatch_pending() == 1
    assert received == ["event-000001"]
    assert bus.pending_count == 0
    assert bus.history == (event,)
