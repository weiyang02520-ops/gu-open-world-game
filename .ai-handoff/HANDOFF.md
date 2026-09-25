# Handoff

## Completed Gate

M2 / TASK-M2-001: **PASS_WITH_NOTES**

Reviewed remote HEAD:

`60b4b776ef18c5992ceb6b7ed3131feac7f17469`

Verified:
- integer deterministic combat timing;
- reaction windows;
- real Gu essence costs;
- body-part injuries and movement impairment;
- flee/disengage;
- perceived-state NPC combat decisions;
- active combat save/resume;
- M1 regressions and final CI.

## Authorized now

M3 / TASK-M3-001 — Information, Memory, Relationships and Rumor.

Read:
1. `.ai/CURRENT_STATE.json`
2. `.ai/ACTIVE_TASK.md`
3. `docs/M3_TASK_SPEC.md`
4. `.ai/MASTER_REVIEW.md`
5. `docs/PRODUCT_DIRECTION.md`
6. `docs/context/AGENT_MEMORY.md`

## Carried notes

- Formalize the M2 visible-state shortcut into a true observation/information boundary.
- Add explicit same-time combat ordering regression coverage.
- Final Gate bookkeeping must use exact final pushed Codex HEAD.

## Stop rule

Finish M3, push and remote-verify, return WAITING_FOR_MASTER / next_actor=chatgpt, then STOP.

M4 is not authorized.
