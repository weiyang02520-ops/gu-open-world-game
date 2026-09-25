# Development Roadmap — M0 to V0.1

> This is the default development direction.
> Individual task packets may refine implementation details, but must not silently change product intent.

## Development philosophy

Prefer **large, coherent work packages** over tiny micro-tasks.

A normal Codex work package should attempt to complete a whole playable / testable loop and should usually include:

- implementation;
- tests;
- smoke scenario;
- documentation;
- state / memory update;
- CI verification;
- commit / push / remote verify.

Do not stop after every small file.
Stop at a meaningful Gate.

If one subtask is blocked, continue independent subtasks when safe, record the blocker, and only stop early when the remaining acceptance criteria genuinely depend on it.

---

# M0 — Deterministic core

Status: PASS

Completed:

- WorldClock
- deterministic RNG
- Entity IDs
- EventBus
- WorldState
- JSON Save / Load
- provenance model
- tests / CI
- agent state / memory / handoff

Purpose:

Create a recoverable deterministic base.

---

# M1 — Day 1–2 Living Sandbox

Status: PASS_WITH_NOTES

Goal:

Prove that a tiny world can live for two days with player and NPCs competing for real resources.

Deliver as one substantial package:

- shared Character model;
- HUMAN / AI controllers;
- aperture / primeval essence minimum;
- three starter Gu;
- hunger / feeding;
- ResourceDefinition / ResourceLot;
- one finite regenerating resource node;
- one finite local market;
- real buy / sell;
- player gather / feed / cultivate;
- 3–5 NPCs with minimal Needs / Goals;
- NPC activity during player idle;
- authoritative event log;
- deterministic Day 1–2 smoke scenario;
- save/resume determinism;
- M0 hardening notes.

Exit condition:

A 48-hour headless simulation demonstrates the whole local loop and remains deterministic.

---

# M2 — Combat, injury and hostile decision loop

Status: COMPLETE_PENDING_MASTER_REVIEW

Goal:

Make the first real hostile encounter emerge from actor state rather than a scripted battle trigger.

Target package:

## Character / body

- body-part minimum model;
- injury states;
- bleeding / impairment minimum;
- death / incapacitation boundary.

## Action pipeline

- ActionIntent;
- validation;
- preparation;
- activation;
- resolution;
- consequence;
- durable event.

## Gu combat use

- enough Gu activation to support:
  - one attack;
  - one movement / escape option;
  - one perception / detection option;
- primeval essence consumption;
- simple activation timing.

## Reaction Window

- detect threat;
- allow evade / defend / flee where valid;
- deterministic test scenario.

## NPC hostile choice

- basic combat-risk estimate;
- attack / avoid / flee;
- no omniscient hidden player data.

## Scenario

At least one encounter can end in:

- win;
- escape;
- injury;
- attacker withdrawal.

Out of scope:

full killer-move editor and advanced path interactions.

Exit condition:

Combat meaningfully changes character state, resources and future NPC decisions.

Delivered in TASK-M2-001:

- integer millisecond ordering and serializable active encounters;
- six-part injuries, bleeding, impairment and movement consequences;
- attack/movement/perception Gu roles and reaction windows;
- visible-state NPC attack/hold/flee decisions;
- deterministic evade, injury, retreat and mid-combat resume scenarios;
- M1 regression and M1/M2 CI smoke coverage.

---

# M3 — Information, memory, relationships and rumor

Status: COMPLETE_PENDING_MASTER_REVIEW

Goal:

World consequences should depend on who actually knows what.

Target package:

- Observation;
- Evidence minimum;
- Report;
- RumorThread;
- BeliefRecord;
- confidence;
- source chain;
- independent-source handling;
- NPC Memory;
- multi-dimensional Relationship;
- information travel time;
- lying / distorted report minimum.

Scenario:

A combat / theft event happens.

Different observers receive different information.
At least one NPC believes an incorrect or incomplete version.
NPC behavior changes because of that belief.

Exit condition:

The world no longer grants NPCs omniscient crime knowledge.

Delivered in TASK-M3-001:

- structured observations, evidence, hypotheses and reports;
- claimed/actual report basis, source credibility and lineage;
- per-NPC beliefs, decay, memories and multidimensional relationships;
- delayed rumor channels, structured mutation and minimal investigation;
- incomplete-information decisions, privacy tests and pending transmission Save/Resume.

---

# M4 — Factions, reputation and institutional response

Goal:

Turn local social consequences into collective action.

Target package:

- 3 local factions / organizations;
- FactionState;
- membership;
- offices;
- institutional belief;
- multi-dimensional Reputation;
- audience-specific reputation;
- official standing;
- FactionCase;
- investigation minimum;
- Proposal;
- simplified political decision;
- FactionMission.

Scenario:

The same player action can produce different reactions from:

- an individual NPC;
- local traders;
- a faction.

Exit condition:

A faction response is explainable from information, interests and internal rules, not a global red-name switch.

---

# M5 — Resource crisis, logistics and local world evolution

Goal:

Make Days 3–5 feel like a changing world.

Target package:

- more resource nodes;
- resource health / over-harvest;
- multiple markets or supply points;
- local price divergence;
- Shipment;
- Caravan;
- route risk;
- trader decision minimum;
- faction reserves / procurement;
- shortage event;
- resource crisis scenario.

Scenario:

A shortage changes:

- prices;
- NPC goals;
- transport;
- crime risk;
- faction action.

Exit condition:

An economic disturbance travels through multiple systems without a scripted quest chain.

---

# M6 — Breakthrough, attainment and deeper cultivation

Goal:

Complete the first meaningful growth arc.

Target package:

- Rank 1 minor stages complete;
- breakthrough conditions;
- forced-breakthrough risk minimum;
- better primeval essence quality handling;
- aptitude implications;
- basic path definitions;
- PathAttainmentState;
- InsightEvent;
- novelty / diminishing repeated insight;
- at least one inheritance / study source;
- faction cultivation support hook.

Scenario:

Player can progress from initial stage toward / into middle stage through time and resource decisions.

Exit condition:

Growth does not rely on generic character XP.

---

# M7 — Gu composition and basic killer-move research

Goal:

Establish the defining long-term combat/build system.

Target package:

- Effect Node catalog minimum;
- Effect Graph;
- Gu effect definitions;
- multi-Gu composition;
- killer-move prototype;
- stability / complexity;
- activation order;
- attainment influence;
- failure / backlash minimum;
- save generated killer move.

Scenario:

Player can discover or construct at least one usable multi-Gu combination and improve its stability.

Exit condition:

The architecture proves killer moves do not need to be hard-coded one by one.

---

# M8 — Integrated Day 1–10 Vertical Slice

Goal:

Turn previous milestones into one playable headless vertical slice.

Target content:

- 20–25 locations or equivalent world graph nodes;
- 12–15 important NPCs;
- abstract supporting NPC population;
- 3–5 factions;
- 30–50 Gu definitions planned, with enough actually active for the slice;
- 15–25 resource nodes;
- 3–4 market/supply hubs where justified;
- trade routes;
- Day 3 resource pressure;
- Day 4 combat possibility;
- Day 5 social consequences;
- Day 6 breakthrough opportunity;
- Day 7 faction attention;
- Day 8 shortage;
- Day 9 player macro influence;
- Day 10 shipment / caravan outcome.

Important:

These day labels are acceptance targets, not forced story beats.
The world may reach equivalent states through different event sequences.

Final V0.1 validation:

Run at least two strategy profiles from the same seed:

A. trade / cooperation / cultivation
B. theft / coercion / misinformation / risk

The final worlds must diverge materially and the event log must explain why.

---

# Post-V0.1 — presentation and expansion

Do not start until the integrated core is judged worth presenting.

Candidate work:

- select UI / engine;
- world map interaction;
- event log / rumor / relationship UI;
- Gu management UI;
- cultivation UI;
- combat pause / targeting;
- killer-move graph UI;
- save management;
- content import pipeline;
- wider South Border expansion;
- canonical NPC timeline integration.

Five Regions / Gu Immortal simulation remains later.
