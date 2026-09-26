# Handoff — V0.1 Final Integration

## Current task override — TASK-V0.1-PLAYABLE-LAYER

The M1–M8 core is already on remote `main`. The playable adapter supplies
PlayerCharacter creation, daily actions, deterministic World Tick, NPC state,
complete pending events, unified Effects, Save/Load/Resume and a 30-day demo
without replacing milestone modules. Final handoff is after push and remote
verification with `WAITING_FOR_MASTER / next_actor=chatgpt`. The playable
implementation code-bearing commit is `61078ee332196f805492b0b6f32d3ae4312bf54b`.

## Active task

`TASK-V0.1-FULL-001`

## Executor model

This repository is executor-agnostic.

ChatGPT Web, Sol, Astre or Codex may continue from the same repository state.

## Completed checkpoints

### M4
Faction / reputation / cases / governance / missions.

### M5
Resource crisis / multi-market economy / Shipment / Caravan / real cargo / route risk.

### M6
Rank1 INITIAL/MIDDLE/UPPER/PEAK, cultivation sessions, safe/forced breakthrough, PathAttainment, Insight and study/inheritance.

Verified checkpoint:
`c5e86027a4c79061b3e4575bc742580432363ed7`

### M7
Serializable Effect Graph, M2 combat wrappers, multi-Gu KillerMove, stability/mastery, backlash, attainment-gated complexity and research improvement.

Verified checkpoint:
`24db39a3131293ea8342994b6d38301232977e4b`

## Current checkpoint

**M8 — Integrated Day1–10 V0.1**

Required final targets:

- 20–40 important local locations;
- 15–30 important NPCs target;
- 3–5 factions;
- 30–50 Gu definitions target;
- 20+ meaningful feeding requirements;
- 15–25 resource nodes;
- 3–4 markets;
- 5–8 routes;
- world LOD;
- CanonAnchor scaffold;
- cooperative/adversarial same-seed runs;
- material divergence across economy, NPCs, factions, cultivation, Gu, killer moves, logistics and future goals;
- event log explaining divergence.

## Handoff behavior

An incoming executor should:

1. pull latest main;
2. read `.ai/CURRENT_STATE.json`;
3. read `docs/EXECUTOR_POLICY.md`;
4. read V0.1 full spec + acceptance matrix;
5. continue M8 directly;
6. avoid redoing M4–M7 unless tests show regression.

## Stop

Only at full V0.1 Gate or a genuine product-level blocker.
