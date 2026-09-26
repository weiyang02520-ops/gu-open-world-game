# M8 Architecture — Integrated Day1–10 V0.1

## Purpose

M8 is the final headless integration layer for V0.1.

It does not replace M1–M7. It composes them into one deterministic local-world simulation:

- M1 Character / Gu / resource / market / WorldClock;
- M2 combat / reaction / body injury;
- M3 Observation / Evidence / Report / Rumor / Belief / Memory;
- M4 factions / cases / reputation / standing / missions;
- M5 resource ecology / markets / Shipment / Caravan;
- M6 Rank1 progression / breakthrough / attainment;
- M7 Effect Graph / killer-move research.

Authoritative state remains the shared WorldState and durable event log.

## Integrated engine

Entry point:

`src/gu_game/m8/engine.py::IntegratedV01Engine`

The M8 layer stores only integration-specific state under:

`WorldState.game_state["m8_integrated"]`

It keeps references to lower-layer engines rather than copying their authoritative state.

## Local world content

V0.1 currently targets a compact Southern-Border-inspired GAME_EXTENSION region.

Integrated content includes:

- 20–40 important location nodes target;
- main settlement and smaller settlements/camps;
- faction headquarters;
- markets;
- resource areas;
- route stops and danger routes;
- hidden inheritance/study location;
- 15+ important NPC profiles;
- 3 active local factions;
- 30–50 Gu definitions target;
- 20 resource nodes;
- 3 markets;
- 6 routes.

Unsupported fictional content remains GAME_EXTENSION.

No full novel text is stored.

## Hierarchical location graph

`LocationNode` stores:

- stable location ID;
- name;
- kind;
- parent;
- neighbors with integer travel minutes;
- simulation level;
- hidden flag;
- provenance.

Travel uses deterministic shortest-path calculation and consumes WorldClock time.

## Simulation LOD

M8 formalizes:

- ACTIVE
- NEAR
- REGIONAL
- ABSTRACT

Player-local content receives finer scheduling.

Remote important NPCs use coarse deterministic scheduling through `RemoteActorState`.

The goal is to prove that a larger future world does not require combat-tick simulation everywhere.

## Remote NPC behavior

Important NPCs retain:

- role;
- faction link;
- home location;
- persistent role/goal tags;
- remote action count;
- last remote action;
- next scheduled action.

M8 distinguishes strategic/social goal consequences from short-term economic needs.

Example:

- strategic goal: WATCH_PLAYER;
- economic need: SECURE_GU_FOOD.

A shortage may change the economic need without erasing the strategic consequence of prior social events.

## Conditional CanonAnchor scaffold

`CanonAnchor` is architectural scaffolding for future canon-timeline integration.

Fields include:

- expected participants;
- location;
- prerequisites;
- earliest/latest day;
- divergence policy;
- provenance;
- source locator;
- status.

V0.1 anchors are GAME_EXTENSION placeholders.

An anchor becomes eligible only when prerequisites and participants are valid.

It is never forced merely because a calendar date is reached.

## Day1–10 systemic windows

The integrated smoke uses ten systemic windows:

1. survival / gathering / trade / feeding;
2. cultivation;
3. resource pressure;
4. combat;
5. observation / report / faction case;
6. breakthrough;
7. faction missions;
8. shortage crisis;
9. killer-move research;
10. caravan outcome.

These are test scenarios, not a mandatory main quest architecture.

The production direction remains freeform systemic play.

## Strategy profiles

Two deterministic acceptance profiles run from the same seed.

### Cooperative

Typical behaviors:

- legal gathering/trading;
- evidence cooperation;
- faction recruitment;
- mission completion;
- safer cultivation;
- support supply;
- protect/enable caravan;
- research stable killer move.

### Adversarial

Typical behaviors:

- hoarding;
- theft;
- aggressive combat;
- suspicion / faction watch;
- forced cultivation risk;
- route pressure;
- caravan robbery;
- riskier killer move.

## Required material divergence

The final same-seed comparison tracks:

- wealth;
- cultivation;
- Gu condition;
- killer move;
- relationships;
- strategic/economic NPC goals;
- combat injury;
- markets;
- resource nodes;
- shipment outcome;
- belief chain;
- faction case;
- faction standing;
- membership / mission / access;
- future proposals.

The V0.1 divergence threshold is intentionally multi-dimensional.

Money alone does not count as success.

## Save / Resume

M8 serializes:

- locations;
- important NPC profiles;
- remote actors;
- CanonAnchor state;
- completed day;
- active strategy;
- flags;
- day history;
- strategic NPC goals.

Lower layers serialize their own state in the same WorldState.

A mid-run save must resume to the same final snapshot and ordered durable event log as uninterrupted execution.

## Final CLI

Single strategy:

```powershell
python -m gu_game --scenario v0.1 --seed 20260925 --strategy cooperative
python -m gu_game --scenario v0.1 --seed 20260925 --strategy adversarial
```

Same-seed comparison:

```powershell
python -m gu_game --scenario v0.1-compare --seed 20260925
```

## Final acceptance tests

`tests/test_m8_v01.py` covers:

- content scale;
- LOD;
- conditional CanonAnchor behavior;
- cooperative Day10;
- adversarial Day10;
- same-seed deterministic replay;
- mid-run save/resume;
- strategy divergence;
- remote-world activity while player is idle.

CI additionally executes all M1–M7 smoke scenarios and the three final V0.1 CLI scenarios.

## Current boundary

V0.1 remains a headless simulation prototype.

Deferred:

- graphical client;
- full canon database;
- Five Regions;
- Gu Immortal mechanics;
- production dialogue/LLM layer;
- multiplayer;
- release packaging.
