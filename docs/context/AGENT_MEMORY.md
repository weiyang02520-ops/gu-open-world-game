# Agent Memory

## Current execution truth

- Repository: `weiyang02520-ops/gu-open-world-game`
- Branch: `main`
- Active task: `TASK-V0.1-FULL-001`
- Execution mode: LONG RUN
- M0–M3: completed/reviewed
- M4: completed as internal checkpoint
- M4 code-bearing commit: `40597c401743dc79aa0baedf126c273507047838`
- M4 Gate-state commit: `9e90c3422fdee5bcb675bc061d26a0aa62b077c9`
- Current internal phase: M5
- No human Gate is required between M4/M5/M6/M7/M8.

## Important correction

A previous Codex run mistakenly reverted CURRENT_STATE to TASK-M4-001 / WAITING_FOR_MASTER despite the user's full-V0.1 authorization.

That stop was procedural, not a product blocker.

The repository has now restored the user's explicit instruction:

**continue automatically to full V0.1.**

## Read order

1. `docs/V0_1_FULL_EXECUTION_SPEC.md`
2. `docs/V0_1_ACCEPTANCE_MATRIX.md`
3. `docs/V0_1_CONTENT_TARGETS.md`
4. `docs/PRODUCT_DIRECTION.md`
5. `docs/DEVELOPMENT_ROADMAP.md`
6. `docs/CODEX_EXECUTION_POLICY.md`
7. `docs/GATE_SHA_PROTOCOL.md`

## Current phase M5

Build the real shortage/logistics loop:

- 15–25 nodes target;
- 3–4 markets target;
- 5–8 routes;
- local price divergence;
- overharvest/node health;
- shipments;
- caravans;
- actual cargo transfers;
- route risk;
- faction reserves/procurement;
- shortage affecting NPC/faction goals;
- save/resume in transit.

Then continue M6/M7/M8 without human review.

## Stop

Only at complete V0.1 or genuine product-level blocker.
