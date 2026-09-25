# Active Task

## TASK-M4-001 — Factions, Reputation, Cases and Institutional Politics

### Execution mode

**LARGE TASK MODE**

M3 has passed Master Review.

Before coding read:

1. `docs/PRODUCT_DIRECTION.md`
2. `docs/DEVELOPMENT_ROADMAP.md`
3. `docs/CODEX_EXECUTION_POLICY.md`
4. `docs/M4_TASK_SPEC.md`
5. `.ai/MASTER_REVIEW.md`
6. `docs/context/AGENT_MEMORY.md`
7. `docs/GATE_SHA_PROTOCOL.md`

### Goal

Implement a local institutional layer where factions act from incomplete information, needs and internal politics rather than a global reputation switch.

Core proof:

```text
individual belief
→ institutional belief
→ case / proposal
→ office-holder disagreement
→ governance resolution
→ official standing / mission / recruitment / sanction
```

while keeping personal opinion, audience reputation, institutional belief and official policy separate.

### Required package

- M3 hardening from M4 spec section 1;
- at least 3 local factions/organizations;
- membership states;
- office authority;
- 2+ blocs/interests in at least one faction;
- FactionNeeds;
- institutional beliefs from delivered information only;
- minimal SocialIdentity;
- audience-scoped multidimensional ReputationVector;
- official FactionStanding;
- FactionCase state machine;
- institutional investigation over M3 evidence;
- FactionProposal;
- deterministic governance / voting;
- InfluenceVector minimum;
- recruitment / watch / sanction / close-case actions;
- faction-generated missions;
- integrated M4 scenarios;
- Save/Resume determinism;
- M1/M2/M3 regression;
- CI M1/M2/M3/M4 smoke;
- docs / Memory / Handoff / Report;
- push and remote verify according to Gate SHA protocol.

### Baseline

Reviewed M3 repair Gate:

`6d291afba23907768725ce9136414b673bdb3533`

### Expanded workload

This task intentionally includes the expanded content targets in M4 spec sections 28–39.

Do not stop after schema/framework completion. Build the full small political environment:
- 3 factions;
- 8–12 important faction-linked NPCs;
- 2 concurrent case chains;
- cross-faction disagreement;
- political leverage actions;
- contribution/favor;
- real access control;
- mission lifecycle;
- NPC institutional actions;
- 24–48h autonomous institutional evolution;
- same-seed cooperative vs adversarial divergence validation.

### Completion

Complete the entire coherent M4 package before returning unless a genuine product-level blocker prevents it.

When complete:

- status = WAITING_FOR_MASTER
- next_actor = chatgpt
- last_codex_commit = final code-bearing implementation commit
- final Gate HEAD verified externally per `docs/GATE_SHA_PROTOCOL.md`
- lock released
- STOP

Do not begin M5.
