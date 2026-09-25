# V0.1 Full Execution Spec — M4 → M8 One-Pass Build

> Task: TASK-V0.1-FULL-001
> Execution mode: LONG-RUN / LARGE TASK / NO HUMAN GATE BETWEEN INTERNAL PHASES
> Baseline reviewed Gate: `6d291afba23907768725ce9136414b673bdb3533`
> Current repository state before this task: M0–M3 complete; M4 not yet implemented.

## 0. Authorization

The user explicitly authorizes completing the entire remaining V0.1 scope in one long Codex/Sol run.

This task **supersedes the old rule that required stopping after M4/M5/M6/M7**.

Internal phase boundaries still exist for architecture and testing, but they are **checkpoint boundaries, not human-review gates**.

Codex/Sol may continue automatically through:

- Phase A = former M4
- Phase B = former M5
- Phase C = former M6
- Phase D = former M7
- Phase E = former M8 / integrated V0.1

Stop only when:

1. the entire V0.1 acceptance matrix is complete; or
2. a genuine product-level blocker requires a human decision; or
3. repository integrity / data-loss / licensing risk makes continuing unsafe.

Routine implementation choices are not blockers.

---

# 1. V0.1 Product Goal

Build a deterministic headless vertical slice of an open-world Gu Master simulation covering roughly **10 in-game days** in one local Southern Border region.

The player is an original Gu Master, not the chosen protagonist.

The world must continue without the player.

The final slice must prove that these systems interact:

```text
Cultivation
↕
Gu ownership / feeding / combat use
↕
Resources / markets / refinement
↕
NPC needs / goals / risk
↕
Combat / injury
↕
Observation / evidence / rumor / belief
↕
Relationships / reputation
↕
Factions / cases / politics / missions
↕
Resource shortages / logistics / caravans
↕
Breakthrough / attainment
↕
Killer-move composition
↕
World evolution across 10 days
```

The point is not content quantity by itself. The point is a small world with deep causal loops.

---

# 2. Non-negotiable Architecture

Keep all previously established invariants:

- authoritative deterministic WorldState;
- dedicated deterministic RNG;
- no wall-clock authority;
- one durable ordered event log;
- Player and NPC share core Character/world rules;
- Canon/Fan/Game provenance remains explicit;
- Canon Database != mutable save-world state;
- NPCs/institutions do not read hidden WorldTruth;
- no generic Character EXP as the core progression;
- no single reputation number for all social meaning;
- no infinite market inventory as the core economy;
- no forced main quest;
- LLM output may never override deterministic legality;
- all unsourced balance values are GAME_EXTENSION.

Do not choose a heavy graphical engine during this task.

Remain headless Python core simulation.

---

# 3. Internal Checkpoint Strategy

Use internal checkpoint commits so long execution remains recoverable.

Recommended sequence:

- CP-A: institutional/faction layer complete
- CP-B: resource crisis/logistics complete
- CP-C: cultivation/breakthrough/attainment complete
- CP-D: Effect Graph/killer-move prototype complete
- CP-E1: integrated 10-day content/world complete
- CP-E2: final strategy-divergence validation and V0.1 Gate

At each checkpoint:

- run relevant tests;
- run all previous smoke scenarios;
- commit;
- push;
- continue automatically.

Do **not** set WAITING_FOR_MASTER at internal checkpoints.

Keep:

```text
status = IN_PROGRESS
next_actor = codex
active_task = TASK-V0.1-FULL-001
```

until final V0.1 Gate.

If CURRENT_STATE schema does not currently support IN_PROGRESS cleanly, extend it in a backward-compatible way.

---

# 4. Phase A — Institutional World (former M4)

Implement all requirements from `docs/M4_TASK_SPEC.md`, including expanded sections 28–39.

This phase must finish:

- M3 carried hardening;
- 3+ local factions;
- 8–12 important faction-linked NPCs;
- memberships;
- offices;
- authority;
- political blocs;
- FactionNeeds;
- Institutional Belief;
- SocialIdentity;
- audience-scoped multidimensional ReputationVector;
- official FactionStanding;
- FactionCase;
- institutional investigation;
- Proposal;
- voting/governance;
- InfluenceVector;
- political leverage actions;
- contribution/favor;
- access control;
- mission lifecycle;
- NPC institutional action;
- 24–48h autonomous institutional evolution;
- cooperative vs adversarial institutional divergence.

### Mandatory M3 hardening inside Phase A

1. Penalize only report sources whose claims are actually contradicted by new evidence.
2. Remove unconditional report-arrival trust gain.
3. Trust increases only from credibility / validation outcomes.
4. Institutional investigation must use deterministic evidence rules, not arbitrary truth injection.

### Phase A checkpoint acceptance

- 3+ factions exist.
- 2 simultaneous cases can evolve.
- 2 officers can disagree for explainable reasons.
- institutional knowledge comes from delivered information.
- player can be WATCHED by one faction, FRIENDLY with another.
- at least one membership/access right changes real available actions.
- at least two missions progress through real lifecycle states.
- 48h idle simulation produces institutional events without player input.
- M1–M4 smoke/tests pass.

Then commit/push CP-A and continue automatically.

---

# 5. Phase B — Resource Crisis, Logistics and World Economy (former M5)

## 5.1 Expand resource content

Target V0.1 resource content:

- 1 currency;
- 10–15 Gu-food resources;
- 20–30 refinement materials;
- 10–20 common plant/beast/mineral resources;
- 3–5 strategic resources;
- 15–25 finite resource nodes;
- 3–4 local markets/supply hubs;
- 5–8 routes/connections.

All content may initially be GAME_EXTENSION placeholders if Canon provenance is not established.

## 5.2 Resource nodes

Expand node state:

- stock;
- capacity;
- health;
- regen rate;
- environmental modifier;
- extraction pressure;
- controller/claim;
- contested state;
- infrastructure;
- workers where needed.

Implement logistic-like bounded regeneration or equivalent deterministic rule.

Overharvest must damage node health and reduce future yield.

## 5.3 Local market dynamics

Markets must maintain real:

- stock;
- currency;
- buy/sell orders or equivalent;
- recent trade history;
- local price state;
- supply/demand;
- taxes/fees where faction-controlled.

Price must not be globally fixed.

NPCs must not read a global perfect price.

Introduce actor-specific MarketBelief if needed.

## 5.4 Demand generation

Demand should come from real future consumption:

- Gu feeding;
- refinement;
- healing;
- faction reserves;
- mission needs;
- caravan restocking.

No arbitrary “+demand because day 8” unless represented as GAME_EXTENSION event pressure.

## 5.5 Logistics

Implement:

- Shipment;
- Caravan;
- cargo as actual ResourceLots / Gu / currency;
- origin;
- destination;
- route;
- departure;
- ETA;
- guards/security;
- route risk;
- status.

Cargo must physically leave origin inventory and arrive at destination inventory only if shipment succeeds.

Loss/robbery must create scarcity.

## 5.6 Route risk

Route risk should depend on state such as:

- recent combat;
- known threats;
- faction control;
- patrol/security;
- shortage pressure;
- criminal activity.

Keep formula deterministic.

## 5.7 Faction economy

Add faction:

- treasury;
- warehouse;
- reserves;
- procurement;
- tax flow;
- strategic resource needs;
- market policy minimum.

Shortage should drive FactionNeed and proposals.

## 5.8 Merchant/NPC logistics behavior

NPCs should be able to:

- buy low / sell high based on their own MarketBelief;
- carry goods;
- choose route;
- avoid risky route;
- fulfill faction procurement;
- fail due to robbery/loss.

Do not need advanced optimization.

## 5.9 Resource crisis scenario

Create a systemic shortage:

```text
node degradation / disease / overharvest
→ supply falls
→ market stock falls
→ price rises
→ Gu-food needs increase urgency
→ NPC goals change
→ theft/competition risk rises
→ faction RESOURCE need rises
→ procurement / guards / caravan proposal
→ shipment outcome changes local market
```

Player must have multiple responses:

- gather;
- buy early;
- import/trade;
- support faction supply;
- speculate/hoard;
- steal;
- rob caravan;
- spread scarcity rumor;
- seek substitute.

At least four must be mechanically distinct.

## 5.10 Phase B checkpoint acceptance

- finite nodes deplete and regenerate;
- overharvest damages future output;
- multiple markets can have different prices;
- real caravan cargo moves between inventories;
- shipment loss changes supply/price;
- shortage changes NPC goals and faction needs;
- market rumors may affect beliefs/actions but not create physical goods;
- save/resume during caravan transit is deterministic;
- M1–M5 smoke/tests pass.

Commit/push CP-B and continue automatically.

---

# 6. Phase C — Cultivation, Breakthrough and Attainment (former M6)

## 6.1 Complete Rank-1 progression

Implement Rank 1 minor stages:

- INITIAL
- MIDDLE
- UPPER
- PEAK

Support:

- aperture capacity;
- aptitude;
- primeval essence quantity;
- essence quality;
- aperture wall stage/progress;
- fatigue;
- health modifiers;
- cultivation method minimum.

Do not introduce generic XP.

## 6.2 Cultivation sessions

Cultivation consumes:

- world time;
- primeval essence;
- rest opportunity;
- potentially resources.

World continues during cultivation.

Fast-forward must process:

- NPC actions;
- market changes;
- rumor delivery;
- faction events;
- caravans;
- Gu hunger.

Important events may interrupt cultivation.

## 6.3 Breakthrough

Implement:

- BREAKTHROUGH_READY state;
- safe attempt;
- delayed attempt;
- support-item/resource-assisted attempt;
- forced attempt.

Normal breakthrough should be primarily condition-driven.

Forced breakthrough may introduce deterministic risk using seeded RNG and GAME_EXTENSION coefficients.

Possible failure consequences:

- injury;
- essence loss;
- wall regression;
- fatigue;
- temporary instability.

## 6.4 Rank effect

Rank/stage should affect:

- essence capacity/quality;
- usable Gu constraints where relevant;
- NPC threat estimate;
- faction recruitment valuation;
- social reputation/standing signals.

Do not make rank a generic universal power score.

## 6.5 Attainment

Introduce PathDefinition / PathAttainmentState.

V0.1 active realms:

- ORDINARY
- QUASI_MASTER
- MASTER

Reserve higher schema values for future but do not simulate them deeply.

Attainment progression comes from InsightEvent:

- combat insight;
- study;
- inheritance;
- experimentation;
- observation;
- refining/combining Gu.

Repeated identical insight must have diminishing novelty.

## 6.6 Knowledge vs attainment

Keep separate:

- knowing a recipe;
- knowing a technique;
- having path attainment.

An NPC/player can know a formula without deep attainment.

## 6.7 Inheritance/study source

Add at least one local study/inheritance source that can produce:

- knowledge;
- insight;
- possibly a recipe or killer-move clue.

Do not create a scripted main quest around it.

## 6.8 Cultivation/faction interaction

Faction may:

- offer cultivation resources;
- restrict resource access;
- sponsor promising members;
- recruit based partly on cultivation;
- assign missions based on perceived strength.

## 6.9 Phase C checkpoint acceptance

- player can progress from Rank1 Initial toward/into Middle through real cultivation;
- cultivation consumes time and essence;
- world evolves during cultivation;
- forced vs safe breakthrough differ;
- aptitude affects aperture capacity, not simple XP gain;
- attainment progresses from InsightEvent;
- repeated insight has diminishing novelty;
- knowledge != attainment;
- save/resume around breakthrough/attainment is deterministic;
- M1–M6 smoke/tests pass.

Commit/push CP-C and continue automatically.

---

# 7. Phase D — Gu Effect Graph and Killer-Move Prototype (former M7)

## 7.1 Goal

Prove that Gu abilities and killer moves can be composed from deterministic effect components rather than hard-coded skill-per-move logic.

## 7.2 Effect Graph

Introduce a minimal Effect Graph system.

Suggested node families:

- CONSUME_ESSENCE
- TARGET
- CHECK_RANGE
- PREPARE
- MOVE
- CREATE_PROJECTILE / EFFECT
- APPLY_FORCE
- APPLY_INJURY
- APPLY_STATUS
- DETECT
- MODIFY_PERCEPTION
- MODIFY_MOVEMENT
- DELAY
- BRANCH_CONDITION
- SEQUENCE
- END

Use only what is needed for V0.1.

Graph execution must:

- validate;
- be deterministic;
- create durable events;
- integrate with M2 combat timing;
- consume real resources/essence;
- serialize.

## 7.3 Gu effect definitions

Migrate or wrap the three M2 combat Gu into Effect Graph definitions without breaking old scenario behavior.

Not every V0.1 Gu needs a complex graph.

Support simple declarative definitions.

## 7.4 Killer-move composition

Introduce KillerMoveDefinition / KillerMoveInstance or equivalent.

Fields should include:

- killer_move_id;
- name;
- core Gu;
- auxiliary Gu;
- path;
- activation order;
- effect graph;
- essence cost;
- preparation time;
- stability;
- complexity;
- mastery;
- provenance.

## 7.5 Composition legality

Check:

- component Gu ownership;
- Gu condition;
- rank compatibility;
- path compatibility;
- essence budget;
- activation ordering;
- attainment requirement;
- conflict score;
- complexity/control burden.

All numeric tuning GAME_EXTENSION unless source-backed.

## 7.6 Stability/mastery

Support:

- DISCOVERED
- UNSTABLE
- USABLE
- PROFICIENT
- MASTERED

For V0.1, at least DISCOVERED→USABLE should be exercised.

Instability may cause:

- fail activation;
- extra essence cost;
- self-injury;
- partial effect;
- Gu strain.

## 7.7 Attainment interaction

Path attainment should affect:

- allowed graph complexity;
- substitution tolerance;
- stability;
- design success;
- interpretation of insight.

Do not simply add flat +damage.

## 7.8 Discovery/research

Support a bounded research loop:

```text
knowledge / clue
+ owned Gu
+ path attainment
+ experimentation time/resources
→ candidate composition
→ test
→ instability/result
→ insight
→ improved version
```

No LLM is required.

LLM naming/description may be added later but cannot determine legality.

## 7.9 Required killer-move scenario

Player owns multiple Gu and can create at least one multi-Gu move.

Example pattern:

- perception component identifies opening;
- movement component repositions;
- attack component resolves;
- combined timing differs from separate manual activation.

Need not be canon.

Clearly label GAME_EXTENSION placeholder move.

## 7.10 Phase D checkpoint acceptance

- Effect Graph serializes;
- graph execution deterministic;
- M2 Gu behavior remains compatible;
- at least one multi-Gu killer move can be created;
- illegal combination is rejected;
- unstable composition can fail/backlash;
- attainment influences legality/stability;
- research can improve stability;
- save/resume killer-move state works;
- M1–M7 smoke/tests pass.

Commit/push CP-D and continue automatically.

---

# 8. Phase E — Integrated Day 1–10 V0.1 (former M8)

This is the final product integration phase.

## 8.1 World content scale

Target local-world content:

### Map
- 20–40 important locations;
- one main settlement;
- 2–4 smaller settlements/powers;
- forests/valleys/river/mine/trade route/resource areas;
- at least one hidden/optional location;
- hierarchical location graph.

### NPCs
- 30 important/medium NPCs target;
- minimum 15 fully detailed important actors if time/complexity requires;
- additional abstract ordinary NPCs;
- mix of gatherers, merchants, faction members, investigators, guards, independent Gu Masters.

### Factions
- 3–5 active factions/organizations.

### Gu
- target 30–50 Gu definitions;
- at least 20 with distinct feeding chains or materially distinct food requirements;
- subset actively exercised by V0.1 systems.

### Economy
- 15–25 resource nodes;
- 3–4 markets;
- 5–8 routes;
- real shipments/caravans.

Do not inflate content with meaningless clones.

## 8.2 10-day systemic arc

Days are acceptance windows, not scripted chapters.

### Days 1–2
Existing living sandbox:
- gather;
- market;
- feed Gu;
- cultivate;
- NPC autonomous actions.

### Day 3
Resource pressure becomes visible:
- Gu food pressure;
- node degradation/shortage;
- price increase;
- multiple response routes.

### Day 4
Combat risk:
- hostile encounter possible from NPC goals/risk;
- injuries/escape possible;
- witnesses create information consequences.

### Day 5
Social/information consequences:
- rumor spreads;
- relationships diverge;
- reputation differs by audience;
- cases may open.

### Day 6
Cultivation opportunity:
- breakthrough readiness;
- safe/forced/delayed options;
- world continues during cultivation.

### Day 7
Faction attention:
- recruitment/watch/investigation/mission possibilities;
- internal disagreement;
- no scripted mandatory quest.

### Day 8
Shortage crisis:
- market stock low;
- prices high;
- factions procure/guard;
- caravans/shipments matter.

### Day 9
Player macro influence:
Possible strategies:
- stabilize supply;
- profit from arbitrage;
- hoard;
- spread information;
- steal;
- attack shipment;
- help faction;
- exploit faction.

### Day 10
External shipment / caravan consequence:
- successful delivery eases shortage;
- loss/attack prolongs crisis;
- official response reflects prior evidence/standing;
- player state diverges strongly.

## 8.3 Canon-divergence scaffold

Add a minimal CanonTimeline/CanonAnchor schema if not present.

Do not import full novel text.

Support structured anchor fields:

- anchor_id;
- expected participants;
- location;
- prerequisites;
- expected time window;
- source/provenance;
- divergence policy;
- status.

V0.1 may include only a few placeholder/non-spoiler local anchors.

Purpose: establish future architecture where canon events are conditional rather than forced.

## 8.4 World LOD

Formalize simulation levels:

- ACTIVE
- NEAR
- REGIONAL
- ABSTRACT

At minimum:

- active combat uses fine ticks;
- current local world uses minute/hour updates;
- remote actors can use hourly/daily aggregated actions.

Verify that remote simulation does not require combat-tick updates.

## 8.5 Player freedom

The final slice must allow at least these action families without a mandatory main quest:

- cultivate;
- gather;
- trade;
- feed Gu;
- investigate;
- share/withhold/lie;
- fight/flee;
- accept/ignore mission;
- seek affiliation;
- steal/rob;
- escort/support shipment;
- research killer move;
- travel between local nodes.

Not every action must be equally optimal.

## 8.6 Two-strategy final validation

From the same seed, run at least two deterministic strategy profiles.

### Profile A — cooperative / stabilizing

Example:

- trade/gather legally;
- share evidence;
- aid faction;
- complete supply/investigation mission;
- cultivate safely;
- help caravan;
- build reliable reputation;
- pursue affiliation.

### Profile B — adversarial / exploitative

Example:

- conceal information;
- manipulate rumor;
- steal/rob;
- hoard/speculate;
- evade faction investigation;
- force cultivation risk;
- attack/redirect caravan;
- use riskier killer move.

The exact strategies may vary.

## 8.7 Required final divergence

By Day 10, the two profiles must materially differ in at least:

- player wealth;
- cultivation stage or breakthrough state;
- primeval essence/resources;
- Gu condition/feeding;
- killer-move knowledge/stability;
- at least 3 NPC relationship states;
- at least 2 NPC goals;
- at least 1 NPC survival/injury state;
- at least 2 market prices/stocks;
- at least 2 resource nodes;
- at least 1 caravan/shipment outcome;
- at least 1 rumor/belief chain;
- at least 1 faction case;
- at least 2 faction standings/reputations;
- at least 1 membership/mission/access state;
- future faction goal/proposal state.

If the main difference is only money or one reputation number, V0.1 fails.

---

# 9. Content Provenance

Do not bulk-ingest the novel.

For V0.1:

- use existing structured provenance model;
- mark unsupported game content GAME_EXTENSION;
- only mark CANON_EXPLICIT when source evidence exists;
- fan/wiki material remains FAN_COMPILED unless confirmed;
- store source locators/summaries, not long copyrighted passages.

If specific canon Gu are needed but evidence is uncertain, prefer placeholder Game Extension Gu rather than falsely marking canon.

---

# 10. Save Compatibility

Maintain/load:

- M1 saves;
- M2 combat saves;
- M3 information saves;
- internal checkpoint saves where practical.

If schema evolves:

- increment schema version;
- implement migrations;
- test representative old saves.

Final V0.1 saves must persist every active domain:

- economy;
- cultivation;
- Gu;
- combat;
- information;
- faction;
- logistics;
- attainment;
- killer moves;
- scheduler/LOD;
- event log.

---

# 11. Performance Bound

This is a prototype, but basic performance matters.

Add at least one deterministic benchmark-style test/smoke for:

- 10 game days;
- target NPC population;
- active factions;
- resource/logistics updates.

No strict milliseconds threshold is required unless stable in CI.

Record:

- event count;
- NPC action count;
- simulation wall time in local report only if desired;
- save size.

Avoid O(N²) full-world scans in every fine combat tick where easy to prevent.

---

# 12. Debuggability

Add developer-visible summaries:

- world summary;
- player summary;
- market summary;
- faction summary;
- rumor/case summary;
- caravan summary;
- cultivation summary;
- killer-move summary.

Final CLI should support something like:

```powershell
python -m gu_game --scenario v0.1 --seed 20260925 --strategy cooperative
python -m gu_game --scenario v0.1 --seed 20260925 --strategy adversarial
```

Exact syntax may differ.

Do not build graphical UI.

---

# 13. CI for Full V0.1

Final CI should run:

1. install;
2. full pytest;
3. M1 smoke;
4. M2 smoke;
5. M3 smoke;
6. M4 smoke;
7. logistics/resource-crisis smoke;
8. cultivation/breakthrough smoke;
9. killer-move smoke;
10. V0.1 cooperative integrated smoke;
11. V0.1 adversarial integrated smoke;
12. deterministic divergence assertions.

Keep runtime reasonable; split jobs if necessary.

---

# 14. Documentation Deliverables

By final Gate, update/create:

- V0.1 architecture overview;
- module map;
- event catalog;
- save schema;
- economy/resource/logistics architecture;
- cultivation/attainment architecture;
- Effect Graph/killer-move architecture;
- faction architecture;
- world LOD/scheduler;
- content/provenance guide;
- CLI/scenario guide;
- testing/acceptance matrix;
- AGENT_MEMORY;
- CHATGPT_MEMORY;
- HANDOFF;
- CODEX_REPORT;
- README.

Keep docs aligned with implemented code.

---

# 15. Internal Review Discipline

Even without human gates between phases, Codex/Sol must perform self-review at each checkpoint.

For each internal phase:

- inspect git diff;
- run previous regressions;
- run new tests;
- check no unauthorized subsystem rewrite;
- update docs;
- commit/push;
- continue.

Do not declare a phase complete based only on code compiling.

---

# 16. Scope Explicitly Deferred Beyond V0.1

Do not implement:

- Gu Immortal systems;
- blessed lands;
- tribulations;
- Treasure Yellow Heaven;
- full Five Regions;
- large-scale sect wars;
- complete canon character roster;
- full canon plot recreation;
- graphical 3D/2D engine;
- production networking/multiplayer;
- LLM-driven authoritative mechanics;
- advanced natural-language dialogue engine;
- full mod marketplace;
- production launcher/updater.

---

# 17. Final V0.1 Gate

Only at the end of the full task:

```text
status = WAITING_FOR_MASTER
next_actor = chatgpt
active_task = TASK-V0.1-FULL-001
```

Use `docs/GATE_SHA_PROTOCOL.md`:

- last_codex_commit = final code-bearing implementation commit;
- Gate bookkeeping commit may follow;
- final remote HEAD verified externally;
- no self-referential SHA loop.

Then STOP.

---

# 18. Final PASS Standard

V0.1 passes only if:

1. the world can run for 10 game days;
2. player can ignore all missions and the world still changes;
3. NPCs act without player input;
4. economy has finite goods and logistics;
5. Gu feeding consumes actual resources;
6. cultivation consumes time/essence and can break through;
7. combat uses reaction/injury, not only HP;
8. information can be wrong and delayed;
9. factions act from institutional belief, not hidden truth;
10. cases can be disputed/closed;
11. reputation/standing/personal relationships remain separate;
12. caravans physically move goods;
13. shortage propagates through multiple systems;
14. attainment exists independently of rank;
15. at least one killer move is composed from multiple Gu/effects;
16. save/resume remains deterministic across active subsystems;
17. cooperative and adversarial same-seed runs diverge materially;
18. event log explains the divergence;
19. all CI/tests/smokes pass;
20. documentation matches reality.

If any subsystem is represented only by empty interfaces/mock flags without affecting the final 10-day world, it does not count as complete.
