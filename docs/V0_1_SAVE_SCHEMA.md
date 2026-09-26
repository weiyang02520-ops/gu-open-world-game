# V0.1 Save Schema

## Root authority

All persistent game data is rooted in `WorldState`.

Current root schema version:

`WorldState.CURRENT_SCHEMA_VERSION = 2`

Root JSON fields:

- `schema_version`
- `world_seed`
- `world_clock`
- `deterministic_rng`
- `entity_ids`
- `entities`
- `event_log`
- `scheduler_queue`
- `canon_divergence`
- `game_state`

## Determinism-critical root state

### WorldClock

Integer elapsed seconds only.

No wall-clock timestamp is authoritative.

### DeterministicRNG

The Python Random internal state is serialized into JSON-safe data.

Save/resume therefore continues the same RNG sequence.

### EntityIdFactory

ID counters are serialized so resumed runs do not reuse IDs.

### event_log

Durable DomainEvents are serialized in exact order.

Save/resume acceptance compares both final state and ordered event log.

## Layered game_state ownership

The current V0.1 uses additive domain layers.

### M1 base game state

Stored directly in the root `game_state` object:

- player ID / NPC IDs;
- Character records;
- GuDefinition / GuInstance;
- ResourceDefinition / ResourceNode;
- LocalMarket;
- M1 schema marker.

M1 is the shared physical-character/economy base.

### `m2_combat`

Owns:

- combat profiles;
- active/resolved CombatEncounter;
- integer millisecond/tick combat state;
- positions;
- pending actions;
- injuries and reaction state.

### `m3_information`

Owns:

- hypotheses;
- observations;
- evidence;
- reports;
- transmissions;
- rumors;
- per-NPC beliefs;
- memories;
- relationships;
- source profiles;
- information sequence state.

### `m4_factions`

Owns:

- faction definitions/states;
- needs;
- memberships;
- offices;
- blocs;
- institutional beliefs;
- social identities;
- reputation vectors;
- official standings;
- cases;
- proposals/votes;
- influence;
- missions.

### `m5_economy`

Owns:

- expanded resource-node condition;
- routes;
- shipments;
- caravans;
- faction economy;
- market beliefs;
- demand;
- shortages;
- economic NPC goals;
- trade history.

### `m6_cultivation`

Owns:

- cultivation profiles;
- methods;
- PathDefinition;
- PathAttainmentState;
- InsightEvent history;
- knowledge;
- study/inheritance sources.

The Character's core Rank/essence/aperture values remain on the shared M1 Character.

### `m7_killer_moves`

Owns:

- effect graphs;
- killer-move definitions;
- killer-move instances;
- combat-effect profile bindings;
- research history.

### `m8_integrated`

Owns only integration-specific state:

- hierarchical LocationNode graph;
- important NPC profiles;
- RemoteActorState / LOD scheduling;
- CanonAnchor scaffold;
- completed day;
- active strategy;
- integrated flags;
- day history;
- persistent strategic NPC goals.

M8 does not duplicate lower-layer authoritative data.

## Backward compatibility

General rules:

1. A save with a root schema newer than the running code is rejected.
2. Older optional subsystem data may be absent; engines bootstrap their layer where appropriate.
3. Newly added fields use defaults in `from_dict` where backward-safe.
4. The Gu starvation-exposure accumulator defaults to zero when loading older GuInstance records.
5. Existing M1/M2/M3/M4/M5/M6/M7 save/resume regression tests remain part of CI.

## Save boundary

The JSON save contains no rendering/UI state.

That is intentional.

A future graphical client should derive presentation state from the saved simulation rather than becoming a second gameplay authority.

## V0.1 final persistence acceptance

The final integrated test requires:

- save after Day 5;
- reload;
- continue through Day 10;
- same final snapshot as uninterrupted run;
- same ordered durable event log as uninterrupted run.

The same policy already exists for subsystem-active checkpoints such as combat, pending information transmission and in-transit Shipment.
