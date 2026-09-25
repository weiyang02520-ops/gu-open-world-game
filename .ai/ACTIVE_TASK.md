# Active Task

## TASK-M1-001 — Day 1~2 Headless Sandbox

### Goal

Build the first actually running two-day local-world simulation on top of the approved M0 deterministic core.

The result must demonstrate this loop without combat or faction systems:

`resource node -> gather/trade -> real inventory -> Gu feeding -> cultivation -> NPC autonomous actions -> market/resource state changes -> time advances`

### Required implementation

1. **Unified Character**
   - One Character model for player and NPC.
   - `controller = HUMAN | AI`.
   - Minimal location, inventory, cultivation/aperture and Gu ownership state.

2. **Cultivation minimum**
   - Aperture capacity / aptitude value.
   - Primeval essence current/max/quality.
   - Wall progress.
   - Cultivate action consumes essence and game time and increases wall progress.
   - No generic character EXP.

3. **Gu minimum**
   - GuDefinition and GuInstance separated.
   - Exactly enough data for three starter Gu instances.
   - Feeding requirement and hunger/satiety state.
   - Hunger changes with world time.
   - Feeding consumes a real ResourceLot.

4. **Economy minimum**
   - ResourceDefinition / ResourceLot.
   - One regenerating ResourceNode with finite stock.
   - One LocalMarket with finite inventory.
   - Buy and sell transfer real resources/currency.
   - A deterministic, intentionally simple local price update is allowed and must be marked GAME_EXTENSION.

5. **NPC minimum**
   - 3–5 NPCs.
   - Minimal Need/Goal logic, not a full planner.
   - NPCs must be able to gather or trade for a reason derived from their state.
   - Player idling must not freeze NPC activity.

6. **Action/event path**
   - Player/NPC world changes must enter through an explicit action/validation/event/state-mutation path.
   - Define one authoritative durable event-log path.
   - Do not let EventBus history and WorldState event_log silently diverge.

7. **Runnable scenario**
   - Provide a deterministic Day 1~2 headless sandbox entry point.
   - A user must be able to run it from the documented command line and inspect a concise final summary/event log.

8. **M0 hardening**
   - Make DomainEvent payload safe from post-publication mutation or document and enforce an equivalent immutable boundary.
   - CI must install the project and run both tests and a smoke command.
   - Clean up the provenance test example so “unverified” evidence is not labeled CANON_EXPLICIT.

### Acceptance criteria

- `python -m pytest` passes.
- GitHub Actions passes.
- Project install command passes.
- Documented Day 1~2 smoke command passes.
- Same seed + same scripted actions => identical final state and ordered durable event log.
- Save at an intermediate point, load, continue => same final result as uninterrupted simulation.
- Player can gather, buy, sell, feed a Gu and cultivate.
- Resource-node stock really decreases when gathered and can regenerate according to the game rule.
- Market stock/currency really transfer; there is no infinite shop inventory.
- Gu hunger progresses with game time; feeding consumes an owned resource lot.
- Cultivation consumes primeval essence, advances wall progress and consumes world time.
- With the player idle for 48 game hours, at least three NPC actions occur and at least one economic/resource value changes.
- All balance constants introduced in this milestone are clearly GAME_EXTENSION.
- No complete combat, rumor, faction politics, refinement, caravans, UI or Day 10 implementation.
- Update Memory/Handoff/Report.
- Commit, push and remote-verify using the exact final commit SHA.
- Finish with `status=WAITING_FOR_MASTER`, `next_actor=chatgpt`, then STOP.

### Baseline

Reviewed M0 commit: `ba27a449af05484a437f46a650b1692fb1d121b2`

### Stop condition

Do not begin M2 without a new Master review and task packet.
