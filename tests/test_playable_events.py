"""Playable event and autonomous NPC contract tests."""

from gu_game.core.rng import DeterministicRNG
from gu_game.event_resolver import EventResolver
from gu_game.event_system import (
    Effect,
    EventResult,
    WorldEvent,
    deserialize_pending_events,
    generate_event,
    resolve_event,
    serialize_pending_events,
)
from gu_game.npc_sim import NPCSimulation, NPCState, default_npcs


def test_pending_event_round_trip_preserves_choice_context() -> None:
    event = generate_event(
        "荒林",
        100,
        DeterministicRNG(1),
        resources={"月兰草": 2},
        day=4,
    )
    assert event is not None
    restored = deserialize_pending_events(serialize_pending_events([event]))[0]
    assert restored.to_dict() == event.to_dict()
    assert resolve_event(restored, restored.options[0]).to_dict() == resolve_event(event, event.options[0]).to_dict()


def test_effect_result_is_json_safe_and_unified() -> None:
    result = EventResult(
        message="changed",
        effects=[Effect("player", "health", -4, "beast")],
    )
    assert EventResult.from_dict(result.to_dict()).to_dict() == result.to_dict()


def test_event_resolver_applies_player_and_world_effects() -> None:
    player = type("Player", (), {"health": 20, "inventory": {}})()
    world = {"danger": 10}
    resolver = EventResolver()
    result = resolver.resolve("beast_trace", "track")
    resolver.apply(result, player=player, world=world)
    assert player.inventory["兽材"] == 1
    assert world["danger"] == 11


def test_npc_tick_is_independent_and_saveable() -> None:
    roster = default_npcs()
    before = [npc.to_dict() for npc in roster]
    actions = [npc.tick(day=2) for npc in roster]
    assert len(actions) == 3
    assert any(item.to_dict() != old for item, old in zip(roster, before))
    restored = NPCSimulation.from_dict(NPCSimulation(roster, day=2).to_dict())
    assert restored.to_dict() == NPCSimulation(roster, day=2).to_dict()


def test_npc_ids_are_stable_for_same_identity() -> None:
    left = NPCState("巡山弟子", "faction_member", "荒林", "patrol")
    right = NPCState("巡山弟子", "faction_member", "荒林", "patrol")
    assert left.npc_id == right.npc_id == left.id
