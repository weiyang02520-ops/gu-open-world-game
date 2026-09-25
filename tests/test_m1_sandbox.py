from pathlib import Path

from gu_game.m1.models import ActionIntent, ActionType, HungerState
from gu_game.m1.scenario import finish_day_two, prepare_day_one
from gu_game.m1.simulation import Simulation


def _event_dicts(simulation: Simulation) -> list[dict]:
    return [event.to_dict() for event in simulation.world.event_log]


def test_bootstrap_has_shared_character_model_and_three_player_gu() -> None:
    simulation = Simulation.new(100)
    player = simulation.characters[simulation.player_id]

    assert player.controller.value == "HUMAN"
    assert len(player.owned_gu_ids) == 3
    assert len(simulation.npc_ids) == 3
    assert all(simulation.characters[npc_id].controller.value == "AI" for npc_id in simulation.npc_ids)
    assert all(
        definition.provenance == "GAME_EXTENSION"
        for definition in simulation.gu_definitions.values()
    )


def test_player_gather_buy_sell_feed_and_cultivate_use_real_state() -> None:
    simulation = Simulation.new(101)
    player_id = simulation.player_id
    player = simulation.characters[player_id]
    initial_node_stock = simulation.resource_nodes[simulation.RESOURCE_NODE_ID].current_stock
    initial_currency = player.currency

    simulation.execute(
        ActionIntent(ActionType.GATHER, player_id, resource_id=simulation.FOOD_RESOURCE_ID, quantity=4)
    )
    assert simulation.resource_nodes[simulation.RESOURCE_NODE_ID].current_stock < initial_node_stock
    assert player.inventory_quantity(simulation.FOOD_RESOURCE_ID) == 4

    simulation.execute(
        ActionIntent(ActionType.SELL, player_id, resource_id=simulation.FOOD_RESOURCE_ID, quantity=1)
    )
    assert player.currency > initial_currency
    market_after_sell = simulation.markets[simulation.MARKET_ID]
    assert market_after_sell.inventory_quantity(simulation.FOOD_RESOURCE_ID) == 19

    before_buy_inventory = player.inventory_quantity(simulation.FOOD_RESOURCE_ID)
    before_market_currency = market_after_sell.currency
    before_market_stock = market_after_sell.inventory_quantity(simulation.FOOD_RESOURCE_ID)
    simulation.execute(
        ActionIntent(ActionType.BUY, player_id, resource_id=simulation.FOOD_RESOURCE_ID, quantity=2)
    )
    assert player.inventory_quantity(simulation.FOOD_RESOURCE_ID) == before_buy_inventory + 2
    assert market_after_sell.inventory_quantity(simulation.FOOD_RESOURCE_ID) == before_market_stock - 2
    assert market_after_sell.currency > before_market_currency

    gu_id = player.owned_gu_ids[0]
    simulation.execute(ActionIntent(ActionType.WAIT, player_id, duration_seconds=6 * 3_600))
    gu = simulation.gu_instances[gu_id]
    assert gu.hunger_state in {HungerState.HUNGRY, HungerState.STARVING, HungerState.CRITICAL}
    before_food = player.inventory_quantity(simulation.FOOD_RESOURCE_ID)
    before_satiety = gu.satiety
    simulation.execute(ActionIntent(ActionType.FEED_GU, player_id, gu_id=gu_id))
    assert player.inventory_quantity(simulation.FOOD_RESOURCE_ID) == before_food - 1
    assert gu.satiety > before_satiety

    before_essence = player.cultivation.primeval_current
    before_wall = player.cultivation.wall_progress
    before_time = simulation.world.clock.elapsed_seconds
    simulation.execute(ActionIntent(ActionType.CULTIVATE, player_id))
    assert player.cultivation.primeval_current < before_essence
    assert player.cultivation.wall_progress > before_wall
    assert simulation.world.clock.elapsed_seconds > before_time


def test_resource_regenerates_and_event_log_is_authoritative() -> None:
    simulation = Simulation.new(102)
    player_id = simulation.player_id
    simulation.execute(
        ActionIntent(ActionType.GATHER, player_id, resource_id=simulation.FOOD_RESOURCE_ID, quantity=5)
    )
    after_gather = simulation.resource_nodes[simulation.RESOURCE_NODE_ID].current_stock
    simulation.advance_time(3_600, run_npcs=False)
    assert simulation.resource_nodes[simulation.RESOURCE_NODE_ID].current_stock == after_gather + 1
    assert tuple(simulation.event_bus.history) == tuple(simulation.world.event_log)
    assert len({event.event_id for event in simulation.world.event_log}) == len(simulation.world.event_log)
    assert any(event.event_type == "RESOURCE_REGENERATED" for event in simulation.world.event_log)


def test_idle_player_does_not_freeze_npcs() -> None:
    simulation = Simulation.new(103)
    before = simulation.summary()
    simulation.execute(
        ActionIntent(ActionType.WAIT, simulation.player_id, duration_seconds=48 * 3_600)
    )
    after = simulation.summary()

    assert all(npc["actions"] >= 3 for npc in after["npcs"])
    assert before["resource_node"] != after["resource_node"] or before["market"] != after["market"]
    assert after["event_types"]["NPC_ACTION_SELECTED"] >= 3


def test_same_seed_and_save_resume_match_uninterrupted_run(tmp_path: Path) -> None:
    first = Simulation.new(104)
    prepare_day_one(first)
    checkpoint = tmp_path / "m1-checkpoint.json"
    first.save(checkpoint)
    finish_day_two(first)

    resumed = Simulation.load(checkpoint)
    finish_day_two(resumed)

    repeat = Simulation.new(104)
    prepare_day_one(repeat)
    finish_day_two(repeat)

    assert first.to_dict() == resumed.to_dict() == repeat.to_dict()
    assert _event_dicts(first) == _event_dicts(resumed) == _event_dicts(repeat)
    assert first.world.clock.day_number == 2
