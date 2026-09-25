# Active Task

## TASK-M3-001 — Information, Memory, Relationships and Rumor

### Execution mode

**LARGE TASK MODE**

M2 has passed Master Review.

Before coding read:

1. `docs/PRODUCT_DIRECTION.md`
2. `docs/DEVELOPMENT_ROADMAP.md`
3. `docs/CODEX_EXECUTION_POLICY.md`
4. `docs/M3_TASK_SPEC.md`
5. `.ai/MASTER_REVIEW.md`
6. `docs/context/AGENT_MEMORY.md`

### Goal

Implement the full bounded M3 information package:

```text
World Event
→ Observation
→ Evidence
→ Report
→ Rumor
→ Belief
→ Memory / Relationship
→ Decision under incomplete information
→ New World Event
```

The same underlying event must be able to produce different beliefs and different NPC behavior.

### Required package

- structured hypotheses;
- rule-gated incomplete observations;
- evidence + support/contradiction;
- reports with claimed vs actual basis;
- deliberate lies without mutating WorldTruth;
- source credibility;
- origin_chain_id / independence_group_id;
- correlated-source discount;
- per-NPC BeliefStore;
- deterministic belief decay;
- MemoryRecord;
- multidimensional relationships;
- RumorThread and delayed channels;
- structured rumor mutation;
- minimal investigation;
- NPC information actions / incomplete-information decisions;
- deterministic M3 smoke;
- pending transmission save/resume equivalence;
- M1/M2 regressions;
- dedicated same-time combat ordering test;
- CI, docs, Memory, Handoff, Report, commit/push/remote verify.

### Baseline

Reviewed M2 remote HEAD:

`60b4b776ef18c5992ceb6b7ed3131feac7f17469`

### Completion

Complete the entire coherent M3 package unless a genuine product-level blocker prevents it.

At Gate:
- WAITING_FOR_MASTER
- next_actor=chatgpt
- last_codex_commit must equal exact final pushed Codex HEAD
- lock released
- STOP

Do not begin M4.
