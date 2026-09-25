# Active Task

## TASK-V0.1-FULL-001 — Complete V0.1 One-Pass Build

### Execution mode

**LONG-RUN / LARGE TASK / NO HUMAN GATE BETWEEN INTERNAL PHASES**

The user explicitly authorized the remaining V0.1 to be completed in one continuous Sol/Codex run.

This task supersedes the earlier requirement to stop after M4, M5, M6 or M7.

### Read first

1. `docs/V0_1_FULL_EXECUTION_SPEC.md`
2. `docs/V0_1_ACCEPTANCE_MATRIX.md`
3. `docs/V0_1_CONTENT_TARGETS.md`
4. `docs/M4_TASK_SPEC.md`
5. `docs/PRODUCT_DIRECTION.md`
6. `docs/DEVELOPMENT_ROADMAP.md`
7. `docs/CODEX_EXECUTION_POLICY.md`
8. `docs/GATE_SHA_PROTOCOL.md`
9. `docs/context/AGENT_MEMORY.md`

### Baseline

Last human-reviewed Gate:

`6d291afba23907768725ce9136414b673bdb3533`

M0–M3 are complete.

M4 code has not started at the moment this full-V0.1 authorization is issued.

### Authorized internal phases

Complete all of these without waiting for another human message:

- Phase A / M4 — factions, reputation, cases, institutional politics
- Phase B / M5 — resource crisis, logistics, caravans, expanded economy
- Phase C / M6 — Rank1 progression, breakthrough, attainment
- Phase D / M7 — Effect Graph and killer-move prototype
- Phase E / M8 — integrated Day1–10 V0.1 world and strategy divergence

### Internal checkpoints

After each phase:

- run phase tests;
- run all previous regressions/smokes;
- review diff;
- update docs/state;
- commit;
- push;
- continue.

Do **not** set WAITING_FOR_MASTER at internal checkpoints.

Keep working on TASK-V0.1-FULL-001.

### Stop conditions

Stop only if:

1. the full V0.1 acceptance matrix is complete; or
2. a genuine product-level decision is required; or
3. continuing risks data loss, repository integrity or licensing/compliance.

Routine implementation decisions are not blockers.

### Final Gate

Only after full V0.1 completion:

- final full pytest PASS;
- all smoke scenarios PASS;
- cooperative/adversarial Day1–10 validation PASS;
- docs and Memory current;
- final code-bearing commit pushed;
- final remote state verified per Gate SHA protocol;
- status = WAITING_FOR_MASTER;
- next_actor = chatgpt;
- STOP.

Do not begin post-V0.1 graphical engine or Gu Immortal scope.
