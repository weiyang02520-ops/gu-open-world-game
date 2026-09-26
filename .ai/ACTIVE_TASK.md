# Active Task

## Current task override — TASK-V0.1-PLAYABLE-LAYER

The M1–M8 headless V0.1 core is already present on remote `main`. This task
adds a stable first playable adapter without replacing those rules.

Delivered scope: PlayerCharacter creation, origin selection, three action
points with day phases, cultivate/explore/gather/trade/rest, deterministic
World Tick, NPC routines, complete pending events, unified Effects,
four-location Qing Mao Mountain outer map, Save/Load/Resume, 30-day demo and
reserved network/server/realtime/multiplayer namespaces.

Completed: full regression, playable and historical smoke, implementation
push and remote verification. Current Gate is `WAITING_FOR_MASTER /
next_actor=chatgpt`. Do not start post-V0.1.

## TASK-V0.1-FULL-001 — Complete V0.1 One-Pass Build

### Execution mode

**LONG-RUN / LARGE TASK / EXECUTOR-AGNOSTIC**

The repository is not tied to Codex.

Authorized executors include:

- ChatGPT Web
- Sol
- Astre
- Codex
- another explicitly user-selected coding executor

The repository state is the source of truth.

## Completed internal checkpoints

- M4 — faction / institutional world
- M5 — resource crisis / logistics / local economy
- M6 — Rank1 progression / breakthrough / attainment
- M7 — Effect Graph / killer-move prototype

## Current internal phase

**M8 — Integrated Day1–10 V0.1**

Current goal:

- integrate all previous systems;
- expand local world content;
- add LOD;
- add CanonAnchor scaffold;
- run cooperative/adversarial same-seed strategies;
- prove material world divergence;
- finish final V0.1 acceptance matrix.

## Required reading

1. `docs/V0_1_FULL_EXECUTION_SPEC.md`
2. `docs/V0_1_ACCEPTANCE_MATRIX.md`
3. `docs/V0_1_CONTENT_TARGETS.md`
4. `docs/PRODUCT_DIRECTION.md`
5. `docs/DEVELOPMENT_ROADMAP.md`
6. `docs/EXECUTOR_POLICY.md`
7. `docs/GATE_SHA_PROTOCOL.md`
8. `docs/context/AGENT_MEMORY.md`

## Executor handoff rule

If another executor takes over:

- pull latest `main`;
- read CURRENT_STATE;
- do not assume previous chat context;
- continue the same active task;
- do not redo completed checkpoints unless regression evidence requires it.

## Real-machine boundary

Use a local executor such as Sol/Astre/Codex only when work depends on:

- local GUI;
- hardware;
- camera/microphone;
- robot/sensor;
- device drivers;
- local-only software;
- real latency/performance measurements;
- physical demonstration.

Pure repository code/tests/docs/assets may be handled directly by ChatGPT Web.

## Final V0.1 Gate only

Only after the full V0.1 acceptance matrix is satisfied:

- full pytest PASS;
- all smokes PASS;
- cooperative/adversarial Day1–10 validation PASS;
- docs/Memory/Handoff/report current;
- final code-bearing commit pushed;
- remote verified per Gate SHA protocol;
- status = WAITING_FOR_MASTER;
- next_actor = chatgpt;
- STOP.

Do not begin post-V0.1 graphical client or Gu Immortal scope.
