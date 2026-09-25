# Agent Memory

## Current execution truth

- Repository: `weiyang02520-ops/gu-open-world-game`
- Branch: `main`
- Current milestone: M2
- Current task: `TASK-M2-001`
- M0: PASS
- M1: PASS_WITH_NOTES
- M1 reviewed HEAD: `4d3523dc0fe42d799b34654e4ca2fe67ede6d82f`
- M2 is authorized.
- Read `docs/PRODUCT_DIRECTION.md`, `docs/DEVELOPMENT_ROADMAP.md`, `docs/CODEX_EXECUTION_POLICY.md`, and `docs/M2_TASK_SPEC.md`.

## User working preference

The user prefers large useful work batches and manual control at major Gates.

Within M2:
- continue through related implementation, tests and docs;
- do not stop for routine micro-decisions;
- do not cross into M3.

## Stable technical constraints

- Python 3.12+
- deterministic WorldClock / RNG
- no global random state
- versioned save schema
- one durable event log
- GitHub remote is cross-agent truth
- unsourced tuning numbers are GAME_EXTENSION
- Player and NPC share Character/world rules
- no generic Character EXP as core progression
- Canon/Fan/Game provenance remains first-class

## M1 delivered baseline

- shared HUMAN / AI Character;
- aperture / primeval essence / wall progress minimum;
- three starter Gu;
- Gu hunger and feeding;
- finite resource node;
- finite market;
- real ResourceLot transfers;
- gather / buy / sell / feed / cultivate / wait action path;
- 3 NPC autonomous Need/Goal actions;
- deterministic Day 1–2 scenario;
- authoritative event log;
- save/resume equivalence.

## M2 architecture requirements

- combat timing must not use M1 hourly NPC cadence;
- use deterministic integer sub-second/equivalent combat ordering;
- serializable active CombatEncounter;
- body-part injuries rather than visible HP-only combat;
- attack / movement / perception Gu roles;
- reaction window before resolution;
- real essence costs;
- local distance / position;
- NPC attack / avoid / flee based on perceived visible state;
- mid-combat save/resume determinism;
- M1 regression preserved.

## M1 review notes

- M1 hourly NPC scheduling remains acceptable for coarse economic simulation.
- CURRENT_STATE bookkeeping must record the exact final Codex HEAD at the next Gate.
- M2 must not introduce omniscient NPC knowledge as a shortcut.

## Common failure modes

- attack becomes only hidden HP subtraction;
- combat resolves instantly with no reaction window;
- using floats for authoritative combat time;
- NPC reads exact hidden player essence/injury values;
- overbuilding full M3 information system;
- overbuilding M7 Effect Graph;
- breaking M1 save/scenario without migration;
- stopping after only one combat file while the bounded package remains incomplete.

## Stop rules

At full M2 completion:
- test / smoke;
- docs / Memory / report;
- commit / push / exact remote verify;
- CURRENT_STATE final Codex HEAD exact;
- WAITING_FOR_MASTER;
- next_actor=chatgpt;
- release lock;
- STOP.
