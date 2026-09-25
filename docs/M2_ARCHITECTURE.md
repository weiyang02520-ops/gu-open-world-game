# M2 Combat Architecture

M2 adds a bounded combat layer over the M1 headless `Simulation`. It does not
replace the M1 economy or introduce the later information, faction or Effect
Graph systems.

## Time model

Combat uses integer `combat_time_ms` with a default `250 ms` tick. Every action
has an integer `execute_at_ms` and a monotonic sequence number. Due actions are
sorted by `(execute_at_ms, sequence)`, so equal-time actions are reproducible
without floating-point time.

`WorldClock` remains authoritative in whole seconds. The encounter records its
starting world second, and completed combat milliseconds advance the clock when
whole seconds are crossed. Event payloads retain `combat_time_ms` so events in
one world second still have reaction-scale ordering.

## Encounter and save state

`CombatEncounter` contains participants, local integer positions, pending
actions, reaction windows, actor body state, status and exit reason. The M2
state is stored under `WorldState.game_state["m2_combat"]`; old M1 saves omit
that key and continue to load normally.

The same `WorldState.event_log` used by M1 receives all combat events through
the existing EventBus durable boundary.

## Body and injury model

The six required body parts are represented explicitly. An injury stores
severity, remaining integrity, bleeding, impairment and fatal/incapacitating
flags. Leg impairment reduces later movement distance; head and torso damage
can incapacitate or end an encounter. Bleeding is ticked during combat and
emits `BLOOD_LOSS_CHANGED` events.

## Gu roles

M2 exposes role profiles over owned M1 Gu instances without implementing the
future M7 Effect Graph:

- `ATTACK`: preparation ticks, range, perceptibility, essence cost and a body-part effect;
- `MOVEMENT`: reaction/flee preparation, movement distance and essence cost;
- `PERCEPTION`: detection strength and essence cost.

These values are in `m2/balance.py` and are explicitly `GAME_EXTENSION`.

## Action and reaction flow

```text
validate intent
→ deduct valid essence / schedule integer action
→ COMBAT_ACTION_DECLARED
→ GU_ACTIVATION_STARTED
→ THREAT_PERCEIVED or THREAT_NOT_PERCEIVED
→ optional REACTION_SELECTED
→ tick ordering
→ GU_ACTIVATED
→ ATTACK_EVADED / ATTACK_MISSED / ATTACK_HIT
→ INJURY_APPLIED / BLOOD_LOSS_CHANGED
→ COMBAT_ENDED when disengaged, incapacitated or dead
```

Failed validation does not deduct essence or mutate positions/body state. A
detected reaction with insufficient essence records a rejected reaction and
the attack continues normally.

## NPC visibility boundary

`PerceivedCombatSnapshot` exposes only local distance, visible target signal,
incoming threat, threat strength, visible movement impairment and escape
feasibility. It does not expose the target's exact primeval essence or hidden
injury dictionary. `choose_npc_action` uses that snapshot plus the NPC's own
state to choose attack, hold/avoid or flee.

## Smoke commands

```powershell
python -m gu_game --scenario day1-2 --seed 20260925
python -m gu_game --scenario m2 --seed 20260925
```

The M2 smoke runs detected evade, landed body-part injury and NPC retreat.
