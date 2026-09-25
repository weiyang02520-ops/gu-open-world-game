# Agent Memory

## Current execution truth

- Repository: `weiyang02520-ops/gu-open-world-game`
- Branch: `main`
- Current milestone: M1
- Current task: `TASK-M1-001`
- M0 was reviewed PASS by External ChatGPT.
- Current authorized direction is the Day 1–2 headless living sandbox.
- Read `docs/PRODUCT_DIRECTION.md`, `docs/DEVELOPMENT_ROADMAP.md` and `docs/CODEX_EXECUTION_POLICY.md` before making broad implementation decisions.

## User working preference

The user prefers **large, useful work batches**.

Do not repeatedly stop for minor implementation choices.
Within an authorized task, continue through related subtasks, tests, documentation and verification.

The user still wants manual project direction at milestone / major-design level.
Do not automatically cross milestone Gates.

## Technical constraints

- Python 3.12+
- standard-library-first core remains preferred while sufficient
- pytest for tests
- deterministic WorldClock and dedicated RNG
- JSON save with schema version
- no wall-clock time in authoritative simulation
- no global random state
- GitHub remote is the durable cross-agent truth
- all game-balance values introduced without source support are GAME_EXTENSION

## Architecture invariants

- Player and NPC use a shared Character direction.
- Canon / Fan / Game provenance remains first-class.
- Canon Database and mutable save-world state must not be merged.
- World changes should move through explicit action / validation / event / state mutation boundaries.
- NPCs must not gain omniscient WorldTruth as later information systems are added.
- Generic Character EXP must not become the central progression mechanic.
- Infinite shops / unexplained resource creation must not become the core economy.
- LLMs may assist language later but do not authorize world-rule violations.

## Current M1 carried requirements

- harden DomainEvent payload immutability;
- establish one authoritative durable event log;
- CI install + test + smoke;
- correct the misleading provenance test example;
- shared HUMAN / AI Character minimum;
- cultivation minimum;
- three starter Gu + feeding;
- finite resource node;
- finite market;
- real inventory transfer;
- 3–5 NPC Needs / Goals;
- deterministic Day 1–2 scenario;
- save/resume equivalence.

## Common failure modes

- turning the game into a quest checklist;
- overbuilding future systems before the current loop works;
- treating planning docs as implemented features;
- treating FAN_COMPILED as CANON_EXPLICIT;
- NPCs reading hidden authoritative state they should not know;
- using a single reputation / morality integer for future social simulation;
- claiming remote verification without checking exact remote SHA;
- stopping after a tiny subtask while most authorized work remains.

## Stop rules

Stop at WAITING_FOR_MASTER when the active milestone acceptance criteria are complete.

Also stop if a remaining decision would change product direction or cross into the next milestone.

Do not start M2 merely because M1 finished locally.
