# Agent Memory

## Current execution truth

- Repository: `weiyang02520-ops/gu-open-world-game`
- Branch: `main`
- Active task: `TASK-V0.1-FULL-001`
- Execution mode: LONG RUN
- M0–M3: completed and reviewed
- Reviewed baseline: `6d291afba23907768725ce9136414b673bdb3533`
- M4 code had not started when full-run authorization was issued.
- M4→M8 are now one continuous authorized task.

## User preference

The user explicitly wants a very large one-shot task for Sol so they can leave it working.

Do not stop after M4/M5/M6/M7.

Do not ask routine implementation questions.

Use internal checkpoint commits and keep going.

## Read order

1. `docs/V0_1_FULL_EXECUTION_SPEC.md`
2. `docs/V0_1_ACCEPTANCE_MATRIX.md`
3. `docs/V0_1_CONTENT_TARGETS.md`
4. `docs/M4_TASK_SPEC.md`
5. `docs/PRODUCT_DIRECTION.md`
6. `docs/DEVELOPMENT_ROADMAP.md`
7. `docs/CODEX_EXECUTION_POLICY.md`
8. `docs/GATE_SHA_PROTOCOL.md`

## Stable invariants

- deterministic simulation;
- one durable event log;
- save/resume;
- player/NPC shared core rules;
- NPC/institutional information cannot bypass M3 truth boundary;
- finite physical resources;
- no generic XP progression;
- no single scalar reputation;
- Canon/Fan/Game provenance;
- no full novel ingestion;
- no graphical engine during V0.1.

## Remaining internal phases

### A / M4
Institutional world:
factions, reputation, cases, politics, governance, missions.

### B / M5
Resource/logistics:
expanded nodes/markets, caravans, shipments, shortage propagation.

### C / M6
Cultivation:
full Rank1 minor stages, breakthrough, attainment, insight.

### D / M7
Gu composition:
Effect Graph, killer-move composition, stability/research.

### E / M8
Integration:
20–40 locations target, 15–30 important NPCs target, 3–5 factions, 30–50 Gu target, Day1–10 simulation, cooperative/adversarial same-seed divergence.

## Stop rule

Only final V0.1 Gate or a true product blocker.

At final Gate:
WAITING_FOR_MASTER / next_actor=chatgpt / STOP.
