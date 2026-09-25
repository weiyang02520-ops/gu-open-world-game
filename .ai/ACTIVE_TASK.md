# Active Task

## TASK-M1-001 — Day 1~2 Headless Living Sandbox

### Execution mode

**LARGE TASK MODE**

Do not stop after a few implementation files.
Within this milestone, continue through the entire coherent M1 package, tests, smoke scenario, docs, CI, commit, push and remote verify unless a genuine hard blocker prevents completion.

Before coding, read:

1. `docs/PRODUCT_DIRECTION.md`
2. `docs/DEVELOPMENT_ROADMAP.md`
3. `docs/CODEX_EXECUTION_POLICY.md`
4. `docs/M1_TASK_SPEC.md`
5. `docs/context/AGENT_MEMORY.md`

### Goal

Build the first actually running two-day local-world simulation on top of the approved M0 deterministic core.

The result must demonstrate:

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
   - Three starter Gu instances for the player.
   - Feeding requirement and hunger/satiety state.
   - Hunger changes with world time.
   - Feeding consumes a real ResourceLot.

4. **Economy minimum**
   - ResourceDefinition / ResourceLot.
   - One regenerating ResourceNode with finite stock.
   - One LocalMarket with finite inventory.
   - Buy and sell transfer real resources/currency.
   - Deterministic local price behavior may be simple but must be GAME_EXTENSION.

5. **NPC minimum**
   - 3–5 NPCs.
   - Minimal Needs / Goals, not the full future planner.
   - NPCs gather or trade for state-derived reasons.
   - Player idling does not freeze NPC activity.

6. **Action/event path**
   - Player and NPC state changes enter through explicit action/validation/event/state-mutation boundaries.
   - Define one authoritative durable event-log path.
   - Do not allow EventBus history and WorldState event_log to silently diverge.

7. **Runnable Day 1–2 scenario**
   - deterministic seed;
   - concise starting state;
   - scripted player path for acceptance;
   - autonomous NPC actions;
   - cross into Day 2;
   - final world summary;
   - durable ordered event summary.

8. **Save / resume**
   - save during the scenario;
   - reload;
   - continue;
   - final state and ordered durable event log must equal uninterrupted execution.

9. **M0 hardening**
   - DomainEvent payload safe from post-publication mutation or equivalent enforced immutable boundary;
   - CI installs project, runs tests and smoke;
   - provenance test no longer labels explicitly unverified evidence as CANON_EXPLICIT.

10. **Documentation**
   - update README with actual M1 run command;
   - document M1 domain model and event flow;
   - update AGENT_MEMORY / HANDOFF / CODEX_REPORT;
   - record discovered design deltas.

### Acceptance criteria

- `python -m pytest` passes.
- GitHub Actions passes.
- clean project install passes.
- documented Day 1–2 smoke command passes.
- same seed + same actions => identical final state and ordered durable event log.
- save/load mid-run => same final state as uninterrupted run.
- player can gather, buy, sell, feed Gu and cultivate.
- resource stock actually decreases and regenerates by rule.
- market inventory/currency transfers are real; no infinite shop.
- Gu hunger advances with game time; feeding consumes owned resource.
- cultivation consumes primeval essence, advances wall progress and consumes world time.
- player idle for 48h still produces at least three NPC actions and at least one economic/resource-state change.
- balance constants are identifiable as GAME_EXTENSION.
- scope does not silently expand into complete combat, rumor, faction politics, refinement, caravans, UI or Day 10.
- final exact SHA is pushed and remote-verified.
- finish with `WAITING_FOR_MASTER`, `next_actor=chatgpt`.
- STOP at Gate; do not begin M2.

### Baseline

M0 review PASS is recorded in `.ai/MASTER_REVIEW.md`.

### User intent carried into this task

The user prefers substantial autonomous work packages so they can leave Codex working and do other things.

Therefore:
- do not ask for routine micro-decisions;
- do not stop after a tiny subtask;
- if one item is blocked, continue independent work where safe;
- return only after the package is genuinely at its Gate or a real blocker requires product-level input.
