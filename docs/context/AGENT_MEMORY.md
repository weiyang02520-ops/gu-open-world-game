# Agent Memory

## Current execution truth

- Repository: `weiyang02520-ops/gu-open-world-game`
- Branch: `main`
- Current milestone: M4
- Current task: `TASK-M4-001`
- M0: PASS
- M1: PASS_WITH_NOTES
- M2: PASS_WITH_NOTES
- M3: PASS_WITH_NOTES
- M4 implementation is complete and waiting for External ChatGPT review.
- Reviewed M3 repair Gate: `6d291afba23907768725ce9136414b673bdb3533`

## User preference

Large useful work packages; manual control at major Gates. Continue through implementation/tests/smoke/docs without routine micro-questions.

## Stable project invariants

- deterministic WorldClock/RNG;
- one durable event log;
- save schema remains versioned;
- Canon/Fan/Game provenance remains explicit;
- player/NPC share world rules;
- NPC/institutions do not read hidden WorldTruth;
- no generic character EXP;
- no single scalar reputation;
- official faction policy distinct from personal opinion;
- no M5 systems in this M4 task.

## M4 delivered baseline

- three local factions with needs, states, memberships and offices;
- political blocs, influence and deterministic governance votes;
- institutional beliefs sourced from delivered M3 reports only;
- social identities, audience-scoped reputation and official standing;
- non-binary cases and deterministic investigation;
- recruitment, standing changes and faction missions;
- integrated M4 smoke and faction Save/Resume.

## Gate SHA

`last_codex_commit` records the code-bearing implementation commit. The final remote Gate HEAD is verified externally under `docs/GATE_SHA_PROTOCOL.md`.

## Stop

At M4 completion: tests + four smoke commands + docs/report → push/remote verify → WAITING_FOR_MASTER / chatgpt → STOP before M5.
