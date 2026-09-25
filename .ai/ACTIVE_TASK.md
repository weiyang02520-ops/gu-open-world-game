# Active Task

## TASK-V0.1-FULL-001 — Complete V0.1 One-Pass Build

### Execution mode

**LONG-RUN / LARGE TASK / NO HUMAN GATE BETWEEN INTERNAL PHASES**

The user explicitly authorized the remaining V0.1 to be completed in one continuous Sol/Codex run.

### Progress already completed inside this task

- Phase A / M4 institutional world: **CHECKPOINT COMPLETE**
- M4 code-bearing checkpoint commit: `40597c401743dc79aa0baedf126c273507047838`
- M4 gate-state commit created by Codex: `9e90c3422fdee5bcb675bc061d26a0aa62b077c9`
- M4 CI: PASS
- M1/M2/M3/M4 smoke: PASS

M4 is now treated as an **internal checkpoint**, not a human-review stop.

### Continue now

Completed internal checkpoint:

**Phase B / M5 — Resource Crisis, Logistics and World Economy**

Evidence: `tests/test_m5_economy.py`, 45-test regression, and `--scenario m5` smoke.

Next internal phase:

**Phase C / M6 — Rank1 progression, breakthrough, attainment**

Then continue automatically:

- Phase C / M6 — Rank1 progression, breakthrough, attainment
- Phase D / M7 — Effect Graph and killer-move prototype
- Phase E / M8 — integrated Day1–10 V0.1 and strategy divergence

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

### Internal checkpoint rule

At M5/M6/M7 completion:

- run phase tests;
- run all previous regressions and smoke;
- diff self-review;
- update docs/Memory;
- commit;
- push;
- keep `status = IN_PROGRESS`;
- keep `next_actor = codex`;
- continue.

Do NOT write WAITING_FOR_MASTER at M5/M6/M7.

### Stop conditions

Stop only when:

1. full V0.1 acceptance matrix is complete; or
2. a genuine product-level decision is required; or
3. repository/data/licensing integrity is at risk.

Routine implementation choices are not blockers.

### Final Gate only

After complete V0.1:

- full pytest PASS;
- all smoke PASS;
- cooperative/adversarial Day1–10 validation PASS;
- docs/Memory/Handoff/CODEX_REPORT current;
- final code-bearing commit pushed;
- remote verified per Gate SHA protocol;
- status = WAITING_FOR_MASTER;
- next_actor = chatgpt;
- STOP.

Do not start post-V0.1 graphical client or Gu Immortal scope.
