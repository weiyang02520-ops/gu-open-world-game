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
- Reviewed M3 repair Gate: `6d291afba23907768725ce9136414b673bdb3533`

Read:

- `docs/PRODUCT_DIRECTION.md`
- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/CODEX_EXECUTION_POLICY.md`
- `docs/M4_TASK_SPEC.md`
- `docs/GATE_SHA_PROTOCOL.md`

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
- no global one-number reputation;
- official faction policy must be distinct from personal opinion.

## Delivered baseline

M1:
- local economy/cultivation/Gu loop.

M2:
- deterministic combat/reaction/injury/flee.

M3:
- observation/evidence/report/rumor/belief;
- credibility/lineage;
- memory/relationships;
- delayed information;
- investigation;
- wrong beliefs and different decisions.

## M4 hard requirements

- 3+ local factions/organizations;
- membership != loyalty != relationship;
- office authority;
- political blocs;
- faction needs;
- institutional belief derived from M3 information only;
- SocialIdentity / alias boundary;
- audience-specific multidimensional reputation;
- official standing;
- cases with non-binary guilt states;
- proposals/voting/governance;
- institutional missions;
- individual/public/institution/official state can disagree;
- save/resume deterministic.

## M3 hardening inside M4

- only truly contradicted source claims lose credibility;
- no unconditional +trust merely because a report arrived;
- institutional investigation must call deterministic evidence-generation rules.

## Gate SHA

`last_codex_commit` is the final code-bearing implementation SHA.
Master verifies actual Gate HEAD externally.

## Stop

At M4 completion: tests + M1/M2/M3/M4 smoke + docs/report → push/remote verify → WAITING_FOR_MASTER / chatgpt → STOP before M5.
