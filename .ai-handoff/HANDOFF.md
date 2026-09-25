# Handoff

## Completed Gate

M3 / TASK-M3-FIX-001: **PASS_WITH_NOTES**

Reviewed Gate HEAD:

`6d291afba23907768725ce9136414b673bdb3533`

M3 now provides:

- incomplete Observation;
- structured Evidence / Hypothesis / Report;
- claimed vs actual report basis;
- evaluator-local SourceProfile credibility;
- correlated source discount;
- delayed channels;
- rumor mutation that changes interpreted Belief;
- per-NPC BeliefStore;
- Memory / directional Relationship;
- investigation via evidence rather than truth reveal;
- deterministic Save/Resume.

## Authorized now

M4 / TASK-M4-001 — Factions, Reputation, Cases and Institutional Politics.

Read:

1. `.ai/CURRENT_STATE.json`
2. `.ai/ACTIVE_TASK.md`
3. `docs/M4_TASK_SPEC.md`
4. `.ai/MASTER_REVIEW.md`
5. `docs/PRODUCT_DIRECTION.md`
6. `docs/context/AGENT_MEMORY.md`

## Carried hardening

- source credibility penalties must only hit actually contradicted claims/sources;
- report arrival must not blindly increase trust;
- institutional investigations must use deterministic M3 evidence rules;
- follow non-self-referential Gate SHA protocol.

## Stop

Finish M4 → test/smoke/docs → push/verify → WAITING_FOR_MASTER / chatgpt → STOP.

M5 is not authorized.
