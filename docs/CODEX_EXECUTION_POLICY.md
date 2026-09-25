# Codex Execution Policy — Large Task Mode

> User preference: fewer interruptions, larger useful batches, strong project direction retained by the repository.

## 1. Default task size

Do not optimize for tiny “15 minute” commits.

Default to a **substantial bounded package** that can occupy a long working session.

A good task usually contains several related implementation slices plus:

- tests;
- deterministic scenario;
- documentation;
- memory update;
- CI;
- commit;
- push;
- remote verification.

The task must still have one coherent product goal.

## 2. Continue independently inside the authorized scope

When a task contains 8–15 clear subtasks, do not stop after completing the first two.

Continue until:

- all acceptance criteria are satisfied; or
- a hard blocker makes remaining criteria impossible; or
- continuing would require crossing into an unauthorized milestone / product decision.

Do not ask the user for routine implementation choices that can be resolved from repository architecture and existing decisions.

## 3. What Codex may decide autonomously

Inside an authorized task, Codex may choose:

- file/module layout;
- helper functions;
- test organization;
- naming of internal implementation types;
- refactors necessary to satisfy acceptance;
- simple GAME_EXTENSION balance constants for test scenarios;
- implementation order.

Record meaningful architectural choices in DECISIONS / AGENT_MEMORY.

## 4. What Codex must not decide alone

Stop before changing:

- core product identity;
- player role;
- “high openness” requirement;
- Canon vs World State separation;
- Player/NPC shared-rule direction;
- deterministic rule-engine authority;
- milestone scope;
- final rendering engine;
- licensing / publication strategy;
- whether a disputed lore claim is Canon;
- major database / engine migration not required by the current task.

## 5. Blocker handling

If one item is blocked:

1. record the blocker;
2. continue other independent work;
3. preserve tests;
4. finish everything still safely possible;
5. only then stop.

Return PARTIAL only when unmet acceptance criteria remain.

## 6. No empty-work loops

If CURRENT_STATE says next_actor is not Codex:

- do not modify files;
- do not create a duplicate PR;
- do not create “heartbeat-only” commits;
- stop cleanly.

If next_actor is Codex and the active task is already completed at remote HEAD:

- do not redo it;
- set / preserve WAITING_FOR_MASTER if appropriate;
- stop.

## 7. Completion definition

A task is not complete because code exists locally.

Completion chain:

implementation
→ tests
→ smoke scenario
→ git diff review
→ documentation/memory
→ secret scan
→ commit
→ push
→ remote verify exact SHA
→ state WAITING_FOR_MASTER
→ STOP

## 8. Reporting style

CODEX_REPORT should summarize:

- what actually changed;
- what was tested;
- which acceptance criteria are proven;
- which are only unit-tested;
- exact final SHA;
- CI status if available;
- remaining risks;
- next Gate.

Do not inflate verification level.

### Gate SHA protocol

Git cannot store its own final commit SHA inside that same commit. Use
`docs/GATE_SHA_PROTOCOL.md`: `CURRENT_STATE.last_codex_commit` records the
code-bearing implementation commit, while the final remote HEAD is verified
externally and recorded in `CODEX_REPORT.md` and the final response.

## 9. Quality preference

Prefer:

- clear domain models;
- deterministic tests;
- explicit state transitions;
- readable data;
- explainable event logs.

Avoid:

- premature framework complexity;
- giant generic abstractions without a real V0.1 use;
- implementing future systems merely because they may someday exist;
- fake completeness through empty interfaces.

## 10. User-attention objective

The repository should carry enough context that the user can leave the project alone during an authorized Codex work package and return to a meaningful deliverable rather than another request for micro-direction.
