# Active Task

## TASK-M2-001 — Combat, Injury and Hostile Decision Loop

### Execution mode

**LARGE TASK MODE**

M1 has passed Master Review.

Before coding read:

1. `docs/PRODUCT_DIRECTION.md`
2. `docs/DEVELOPMENT_ROADMAP.md`
3. `docs/CODEX_EXECUTION_POLICY.md`
4. `docs/M2_TASK_SPEC.md`
5. `.ai/MASTER_REVIEW.md`
6. `docs/context/AGENT_MEMORY.md`

### Goal

Implement the complete bounded M2 package in `docs/M2_TASK_SPEC.md`.

The proof should be:

```text
hostile intent
→ preparation / Gu activation
→ perception
→ reaction window
→ movement / evade or failure to react
→ resolution
→ body-part injury / escape
→ durable events
→ changed later combat choices
```

### Required package

- deterministic sub-second/equivalent integer combat timing;
- serializable CombatEncounter;
- body-part injury model;
- attack / movement / perception Gu roles;
- reaction window;
- local distance/position;
- real primeval essence costs;
- NPC attack / avoid / flee risk decision from perceived visible state;
- deterministic combat scenarios;
- mid-combat save/resume equivalence;
- M1 regression;
- CI install/test/M1 smoke/M2 smoke;
- docs, Memory, Handoff, Report;
- commit, push, remote verify.

### Carried constraints

- Do not reuse M1 hourly NPC cadence as combat timing.
- Do not use hidden exact target state in NPC combat decisions.
- Do not implement persistent M3 Belief/rumor early.
- Do not implement M7 full Effect Graph early.
- Preserve M1 saves or add explicit tested migration.
- Record exact final Codex HEAD in CURRENT_STATE before Gate.

### Baseline

Reviewed M1 remote HEAD:

`4d3523dc0fe42d799b34654e4ca2fe67ede6d82f`

### Completion

Execution status: COMPLETE; waiting for External ChatGPT review.

M2 remains bounded to combat, injuries, reaction and visible-state hostile decisions. M3 information/rumor and M7 Effect Graph systems were not started.

Complete the entire coherent M2 package before returning unless a genuine product-level blocker prevents it.

When complete:

- WAITING_FOR_MASTER
- next_actor=chatgpt
- exact final SHA recorded
- lock released
- STOP

Do not begin M3.
