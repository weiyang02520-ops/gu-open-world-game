# Active Task

## TASK-M3-FIX-001 — M3 Semantic Repair

### Execution mode

**LARGE TASK MODE / BOUNDED REPAIR**

M3 implementation is structurally strong but did not pass Master Review due to semantic defects that would contaminate M4 faction behavior.

Read:

1. `.ai/MASTER_REVIEW.md`
2. `docs/M3_REPAIR_SPEC.md`
3. `docs/M3_TASK_SPEC.md`
4. `docs/M3_ARCHITECTURE.md`
5. `docs/PRODUCT_DIRECTION.md`
6. `docs/CODEX_EXECUTION_POLICY.md`

### Goal

Repair M3 semantics without starting M4.

Required focus:

- correct directional relationship updates;
- make SourceProfile dimensions operational;
- connect relationship/source credibility to report impact;
- update source credibility after evaluator-specific contradiction;
- make structured rumor mutation affect interpreted belief;
- strengthen multi-hop lineage/correlation tests;
- define mixed rumor/direct-evidence decay category semantics;
- keep investigation evidence-producing rather than truth-revealing;
- resolve the impossible self-referential Gate SHA protocol truthfully;
- preserve all M1/M2/M3 regressions and Save/Resume determinism.

### Baseline

Reviewed M3 Gate:

`d13f7e71e5a7fa597c5d54efcc25d385eca54c09`

### Completion

Follow `docs/M3_REPAIR_SPEC.md` completely.

At completion:
- all tests/smokes/CI pass;
- status = WAITING_FOR_MASTER;
- next_actor = chatgpt;
- Gate reporting is truthful under the revised non-self-referential SHA semantics;
- STOP.

Do not begin M4.
