# Executor Policy — Large Task Mode

> This repository is executor-agnostic.
>
> The active executor may be ChatGPT Web, Sol, Astre, Codex, or another authorized coding agent.
> The repository state — not the model name — is the source of truth.

## 1. Executor identity

Read `.ai/CURRENT_STATE.json`.

- `next_actor = chatgpt`: ChatGPT Web is the active developer.
- `next_actor = executor`: any explicitly user-selected executor agent may continue.
- legacy `next_actor = codex`: treat as `executor` unless a newer state overrides it.

Do not refuse work merely because this document was historically named CODEX_EXECUTION_POLICY.

## 2. Default work size

Prefer a substantial coherent package:

implementation
→ tests
→ deterministic smoke
→ docs / memory
→ CI
→ commit / push
→ remote verification.

Do not stop after tiny substeps.

## 3. Authorized autonomy

Within the active task, the executor may choose:

- module layout;
- helper functions;
- test organization;
- internal type names;
- refactors required by acceptance criteria;
- GAME_EXTENSION tuning values;
- implementation order.

Record major architecture decisions.

## 4. Decisions requiring user/product authority

Do not silently change:

- product identity;
- player role;
- high-openness requirement;
- Canon vs WorldState separation;
- player/NPC shared-rule direction;
- deterministic rule authority;
- final rendering engine;
- licensing/publication strategy;
- disputed Canon classification;
- milestone scope outside the active authorization.

## 5. Blocker handling

If one item is blocked:

1. record it;
2. continue independent work;
3. keep tests healthy;
4. finish everything still safely possible;
5. stop only if the remaining work truly requires a product-level decision.

## 6. Verification

Never claim completion from code alone.

Required chain:

implementation
→ tests
→ smoke
→ diff review
→ docs/memory
→ CI
→ push
→ remote verification.

## 7. Gate SHA

Follow `docs/GATE_SHA_PROTOCOL.md`.

A commit cannot contain its own SHA.

`last_codex_commit` is retained as a legacy field name for compatibility and means:

**last code-bearing external-executor implementation commit**

For ChatGPT Web direct development, use `last_chatgpt_commit` when useful; external Master review resolves actual remote HEAD directly.

## 8. Reports

`.ai/CODEX_REPORT.md` is a legacy filename.

Any executor may update it. Treat its semantic name as **EXECUTOR_REPORT**.

Report:

- actual changes;
- tests;
- acceptance evidence;
- implementation SHA;
- CI result;
- risks;
- next checkpoint.

## 9. Quality

Prefer deterministic, readable domain code and explicit state transitions.

Avoid:

- fake interface-only completion;
- premature generic frameworks;
- hidden omniscience;
- duplicate authorities for the same state;
- future-system overbuild not exercised by V0.1.

## 10. User-attention objective

The repository must contain enough direction for the active executor to work for a long session without repeatedly asking the user routine questions.

## 11. Real-machine boundary

Use Codex/Sol/Astre on the user's machine only when the task truly depends on:

- local GUI interaction;
- hardware;
- camera/microphone;
- robot/sensor;
- device driver;
- local-only proprietary software;
- real performance/latency measurements;
- physical demonstration.

Pure repository code, tests, docs, CI and generated project assets may be handled directly by ChatGPT Web.
