"""M2 combat tuning values.

Every value here is a GAME_EXTENSION. The values define a deterministic
prototype combat loop and are not claims about source-lore numbers.
"""

GAME_EXTENSION_COMBAT_BALANCE: dict[str, int] = {
    "combat_tick_ms": 250,
    "attack_preparation_ticks": 4,
    "movement_preparation_ticks": 1,
    "perception_preparation_ticks": 1,
    "attack_essence_cost": 8,
    "movement_essence_cost": 5,
    "perception_essence_cost": 3,
    "attack_range": 8,
    "attack_power": 35,
    "attack_perceptibility": 60,
    "movement_distance": 6,
    "flee_distance_multiplier": 2,
    "disengage_distance": 12,
    "perception_strength": 90,
    "bleeding_injury_threshold": 20,
    "heavy_injury_threshold": 30,
    "critical_injury_threshold": 70,
    "fatal_integrity_threshold": 0,
    "npc_risk_tolerance": 40,
    "npc_flee_essence_floor": 4,
}
