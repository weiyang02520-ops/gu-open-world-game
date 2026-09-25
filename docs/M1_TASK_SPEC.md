# M1 Task Spec — Day 1~2 Sandbox

## Product question M1 must answer

Can the approved deterministic core support a small but real living loop where the player and NPCs consume the same world resources over two game days?

M1 is successful only if the answer is demonstrated by executable state transitions, not documentation alone.

## Scenario

A tiny local area contains:

- one player Gu Master;
- 3–5 NPC Gu Masters / local actors;
- one finite regenerating resource node;
- one local market;
- one currency;
- one Gu-food resource;
- three starter Gu instances owned by the player;
- minimal primeval essence and aperture state.

The player may gather, trade, feed Gu, cultivate or idle. NPCs continue acting while the player does nothing.

## Architecture constraints

- Character is shared by HUMAN and AI controllers.
- GuDefinition and GuInstance are distinct.
- ResourceDefinition and ResourceLot are distinct.
- Inventory is authoritative: resources cannot appear during trade without an explicit production/transfer event.
- Core simulation remains headless.
- World time is authoritative.
- No global Python random state.
- Every game-balance number introduced here is GAME_EXTENSION.
- NPC decisions may read their local state; do not introduce the later omniscient Belief/Information system prematurely.

## Required durable event types

At minimum, implement structured equivalents of:

- RESOURCE_GATHERED
- RESOURCE_REGENERATED
- MARKET_BUY
- MARKET_SELL
- GU_HUNGER_CHANGED or a documented periodic equivalent
- GU_FED
- CULTIVATION_STARTED / CULTIVATION_PROGRESS or a documented equivalent
- NPC_ACTION_SELECTED

Exact naming may differ if documented consistently.

## Deterministic acceptance scenario

Provide a scripted/test scenario that:

1. starts from a known seed;
2. gathers from the finite resource node;
3. trades with the finite local market;
4. advances enough time for Gu feeding pressure to change;
5. feeds a Gu from owned inventory;
6. cultivates and spends primeval essence;
7. lets NPCs act without player input;
8. crosses into Day 2;
9. saves and resumes mid-run;
10. verifies resumed and uninterrupted final snapshots match.

## M0 review notes that become M1 requirements

- Harden DomainEvent payload immutability.
- Choose one authoritative event-log path.
- Extend CI to install + test + smoke.
- Remove the misleading CANON_EXPLICIT/unverified provenance test pairing.

## Out of scope

- combat and wounds;
- killer-move composition;
- investigation, evidence, rumors and Beliefs;
- faction politics and reputation;
- full refinement;
- caravans / shipments;
- graphical UI;
- full five-region world;
- Gu Immortal systems;
- Day 3–10 content.

## Gate

At completion, Codex must push and remote-verify the exact final SHA, set WAITING_FOR_MASTER / next_actor=chatgpt, and STOP.

## Implementation entry point

Run the deterministic headless scenario with:

```powershell
python -m gu_game --scenario day1-2 --seed 20260925
```

The command prints a concise Day 2 summary and the tail of the durable event log.
