"""M1 tuning values.

Every number in this module is a GAME_EXTENSION. None of these values claim
to be an explicit fact from the source novel; they only make the sandbox
playable and testable.
"""

GAME_EXTENSION_BALANCE: dict[str, int] = {
    "default_rank": 1,
    "default_aptitude": 60,
    "default_aperture_capacity": 100,
    "default_primeval_current": 60,
    "default_primeval_maximum": 100,
    "default_essence_quality": 1,
    "default_wall_progress": 0,
    "default_wall_threshold": 100,
    "default_resource_value": 1,
    "default_resource_quality": 1,
    "default_gu_condition": 100,
    "world_tick_seconds": 60,
    "gather_duration_seconds": 3_600,
    "market_trade_duration_seconds": 1_800,
    "feed_duration_seconds": 900,
    "cultivate_duration_seconds": 10_800,
    "cultivate_essence_cost": 8,
    "cultivate_wall_progress": 12,
    "resource_initial_stock": 36,
    "resource_capacity": 48,
    "resource_regeneration_per_hour": 1,
    "player_starting_currency": 40,
    "npc_starting_currency": 24,
    "market_starting_currency": 240,
    "market_starting_food_lots": 18,
    "market_food_base_price": 4,
    "market_max_price_shift": 6,
    "gu_starting_satiety": 72,
    "gu_satiety_max": 100,
    "gu_feed_quantity": 1,
    "gu_feed_satiety_gain": 36,
    "gu_hunger_per_hour": 8,
    "gu_starvation_condition_loss_per_hour": 1,
    "npc_count": 3,
}
