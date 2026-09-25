# M2 Task Spec — Combat, Injury and Hostile Decision Loop

> Execution mode: LARGE TASK MODE
> Reviewed M1 baseline: `4d3523dc0fe42d799b34654e4ca2fe67ede6d82f`

## Product question

Can the current living sandbox support a deterministic hostile encounter where Gu activation, perception, reaction timing, primeval essence, movement and injuries all matter, without reducing combat to a visible HP bar?

M2 is complete only when this is demonstrated by executable scenarios, durable events and save/resume determinism.

## 1. Required package

Deliver one coherent M2 package containing:

- deterministic combat timing with integer sub-second ordering or an equivalent no-float representation;
- serializable active CombatEncounter state;
- body-part injuries and bleeding/impairment;
- minimal attack, movement and perception Gu roles;
- preparation / activation / reaction / resolution pipeline;
- local distance or position model;
- real primeval essence costs;
- NPC ATTACK / AVOID / FLEE choice from a perceived visible-state boundary;
- deterministic combat scenarios;
- mid-combat save/resume equivalence;
- M1 regression preservation;
- CI + docs + Memory + Handoff + final remote verification.

## 2. Combat time

M1's one-NPC-decision-per-game-hour cadence is intentionally coarse and must not become combat timing.

M2 must support reaction-scale ordering, roughly 250 ms resolution or another documented deterministic integer model.

Requirements:

- no authoritative floating-point time;
- deterministic ordering for events occurring in the same world second;
- preserve or explicitly migrate M1 saves;
- reconcile combat time with authoritative WorldClock;
- regression tests for old second-based M1 behavior.

Codex may choose the exact internal representation.

## 3. Combat encounter

Introduce a serializable encounter state equivalent to:

```text
CombatEncounter
- encounter_id
- location_id
- participants
- combat_time / tick
- local positions or distances
- pending actions
- perception/reaction state
- encounter status
- exit reason
```

Minimum status:

- ACTIVE
- DISENGAGED
- INCAPACITATED_END
- DEATH_END

An ACTIVE encounter must survive save/load.

## 4. Body / injury model

Minimum body parts:

- HEAD
- TORSO
- LEFT_ARM
- RIGHT_ARM
- LEFT_LEG
- RIGHT_LEG

Injury state must support at least:

- severity;
- bleeding;
- impairment;
- incapacitating / fatal boundaries.

Internal integrity numbers are allowed, but durable events and summaries should expose concrete injuries rather than only HP.

At least one injury must mechanically affect later movement, fleeing, activation or action availability.

All thresholds are GAME_EXTENSION unless source-backed.

## 5. Minimal Gu combat roles

Do not implement the M7 full Effect Graph yet.

Extend the Gu model only enough to prove:

### Attack Gu
- essence cost;
- preparation/activation time;
- range;
- injury/effect profile;
- perceptibility / telegraph value.

### Movement Gu
- reposition / evade / flee;
- essence cost;
- activation time;
- movement effect.

### Perception Gu
- changes whether the defender notices an incoming hostile action early enough to react.

Keep GuDefinition and GuInstance separate.

## 6. Action pipeline

Combat must follow an explicit flow:

```text
ActionIntent
→ Validation
→ Preparation
→ Activation
→ Perception
→ Reaction Window
→ Resolution
→ Consequences
→ Durable Event
```

Minimum intents may include:

- ACTIVATE_ATTACK_GU
- USE_MOVEMENT_GU / EVADE
- FLEE
- HOLD / WAIT

Validation must check ownership, usable state, essence, range, target and body constraints.

Failed validation must not partially mutate authoritative state.

## 7. Reaction Window

Hard requirement.

At least prove:

1. defender detects an attack and successfully evades;
2. defender fails to detect or reacts too late and is injured;
3. defender detects the attack but lacks essence for the intended reaction.

Reaction must change the final attack result where appropriate.

## 8. Local distance / position

M2 does not need a graphical world map.

Use a deterministic integer representation sufficient for:

- attack range;
- movement;
- evade;
- flee;
- disengagement.

## 9. NPC hostile decision

Implement a minimal M2 risk layer, not the future full information planner.

NPC may choose:

- ATTACK
- AVOID / HOLD
- FLEE

Inputs may include:

- own injuries;
- own essence;
- own usable Gu;
- directly perceivable target signals;
- local distance;
- escape feasibility;
- GAME_EXTENSION risk tolerance.

Important:

NPC must not read hidden exact player state merely because it exists in WorldState.

Create a small perceived-combat snapshot or equivalent visibility boundary.

Do not implement persistent M3 Rumor / Belief systems yet.

## 10. Durable combat events

Implement structured equivalents of:

- COMBAT_STARTED
- COMBAT_ACTION_DECLARED
- GU_ACTIVATION_STARTED
- THREAT_PERCEIVED / THREAT_NOT_PERCEIVED
- REACTION_SELECTED
- GU_ACTIVATED
- ATTACK_EVADED / ATTACK_MISSED / ATTACK_HIT
- INJURY_APPLIED
- BLOOD_LOSS_CHANGED where relevant
- FLEE_ATTEMPTED
- COMBAT_ENDED

Exact naming may differ if consistently documented.

Use the M1 authoritative WorldState event log.

## 11. Required scenarios

### Scenario A — detected attack and evade
- hostile action declared;
- target perceives it;
- target uses movement Gu;
- position/distance changes before resolution;
- original injury is avoided;
- both sides spend only valid resources.

### Scenario B — attack lands
- defender fails perception or cannot react;
- attack lands;
- a specific body part is injured;
- final summary exposes the injury;
- injury has a real mechanical consequence.

### Scenario C — hostile NPC retreats
- NPC evaluates the visible encounter state;
- chooses FLEE because the perceived risk is too high;
- encounter can end without forced death.

At least one scenario must reuse/coexist with M1 world state rather than being a disconnected toy simulation.

## 12. Determinism / save-resume

Prove:

- same seed + same intents => identical final state;
- same ordered durable events;
- save during ACTIVE combat;
- reload and continue;
- resumed result equals uninterrupted result.

Persist all required combat state, including pending actions/ticks, positions, injuries, essence and encounter status.

## 13. M1 regression

Keep the Day 1–2 sandbox working.

Required:

- old tests remain passing or are migrated with equivalent coverage;
- Day 1–2 smoke still works;
- market/resources remain finite;
- no generic Character EXP;
- no infinite combat resource generation;
- old save format remains loadable or has explicit tested migration.

## 14. CI

CI must run:

1. project install;
2. full pytest;
3. M1 Day 1–2 smoke;
4. at least one M2 combat smoke.

## 15. Documentation

Update/add:

- M2 architecture;
- combat time model;
- injury/body model;
- reaction pipeline;
- visible/perceived combat-state boundary;
- CLI commands;
- AGENT_MEMORY;
- CHATGPT_MEMORY if direction materially changes;
- HANDOFF;
- CODEX_REPORT.

## 16. Explicitly out of scope

Do not implement:

- persistent Observation / Evidence / Report / Rumor / Belief engine;
- faction cases / reputation / politics;
- full Effect Graph;
- killer-move editor;
- refinement;
- caravan/logistics system;
- graphical combat UI;
- full map;
- Gu Immortal combat;
- canonical major-character AI.

## 17. PASS criteria

M2 PASS requires:

- M1 regressions pass;
- deterministic sub-second/equivalent integer combat ordering;
- active encounter save/load;
- attack Gu consumes essence;
- evade/movement consumes essence;
- perception controls reaction availability;
- reaction can change outcome;
- body-part injury is produced and has mechanical consequence;
- combat can end by flee/disengage, not only death;
- NPC attack/avoid/flee uses a non-omniscient perceived-state boundary;
- same seed/inputs reproduce exact state/event order;
- mid-combat resume equals uninterrupted execution;
- CI install/test/M1-smoke/M2-smoke passes;
- all new tuning values are GAME_EXTENSION;
- no M3+ scope creep;
- docs / Memory / Handoff / CODEX_REPORT updated;
- exact final Codex HEAD is recorded, pushed and remote-verified;
- CURRENT_STATE ends WAITING_FOR_MASTER / next_actor=chatgpt;
- STOP before M3.

## Quality bar

Do not pass M2 merely because an attack function subtracts an internal number.

The meaningful proof is:

> attacker spends essence and time, defender may detect the action, defender may react with a movement Gu, local position changes before resolution, and a landed attack creates a concrete injury that changes later options.
