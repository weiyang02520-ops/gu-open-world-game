# V0.1 Acceptance Matrix

> This matrix is the final truth table for TASK-V0.1-FULL-001.
> Mark items only when executable evidence exists.

## A. Core / Determinism

- [ ] Full pytest passes.
- [ ] Same seed + same scripted actions => identical final snapshot.
- [ ] Save/resume at multiple subsystem-active points => identical continuation.
- [ ] Event ordering deterministic.
- [ ] No authoritative wall-clock use.
- [ ] No global unseeded random.
- [ ] Old M1/M2/M3 representative saves remain loadable or migrated.
- [ ] Gate SHA protocol followed truthfully.

## B. Character / Cultivation

- [ ] Player/NPC share Character core.
- [ ] Rank1 INITIAL/MIDDLE/UPPER/PEAK represented.
- [ ] Aptitude/aperture capacity represented.
- [ ] Primeval essence quantity and quality distinct.
- [ ] Cultivation consumes time and essence.
- [ ] World advances while cultivating.
- [ ] Breakthrough readiness exists.
- [ ] Safe breakthrough path exists.
- [ ] Forced breakthrough path exists with risk.
- [ ] At least one breakthrough changes stage.
- [ ] No generic Character EXP drives cultivation.

## C. Attainment / Knowledge

- [ ] At least one active PathDefinition.
- [ ] PathAttainmentState exists.
- [ ] ORDINARY / QUASI_MASTER / MASTER supported.
- [ ] InsightEvent exists.
- [ ] repeated identical insights have diminishing novelty.
- [ ] knowledge and attainment are separate.
- [ ] inheritance/study source can create knowledge/insight.

## D. Gu

- [ ] GuDefinition != GuInstance.
- [ ] 30–50 Gu definitions target; minimum meaningful active subset documented.
- [ ] 20+ distinct feeding chains/requirements target.
- [ ] hunger advances with time.
- [ ] feeding consumes actual ResourceLot.
- [ ] starvation/poor feeding has real condition consequences.
- [ ] combat Gu consume real essence.
- [ ] Gu condition/state persists in save.

## E. Effect Graph / Killer Move

- [ ] Effect Graph data model exists.
- [ ] effect graph serializes.
- [ ] deterministic graph execution.
- [ ] legacy/simple M2 Gu behavior compatible.
- [ ] at least one multi-Gu killer move.
- [ ] illegal composition rejected.
- [ ] stability represented.
- [ ] instability can fail/backlash.
- [ ] attainment affects legality/stability.
- [ ] research/experimentation can improve move.
- [ ] move persists in save.

## F. Economy / Resources

- [ ] 1 currency.
- [x] finite inventories.
- [x] 15–25 resource nodes target.
- [x] node stock/capacity/health.
- [x] deterministic regeneration.
- [x] overharvest harms future output.
- [x] 3–4 markets target.
- [x] local supply/demand pricing.
- [x] at least two markets can diverge in price.
- [x] NPCs trade real inventory.
- [x] Gu feeding/refinement/faction demand influence markets.
- [x] no infinite-shop core behavior.

## G. Logistics

- [x] Shipment state.
- [x] Caravan state.
- [x] cargo is actual world inventory.
- [x] 5–8 routes target.
- [x] route travel consumes time.
- [x] route risk stateful.
- [x] successful shipment moves stock.
- [x] lost shipment removes/delays stock.
- [x] market prices react to shipment outcome.
- [x] save/resume while in transit deterministic.

## H. Combat

- [ ] integer sub-second/equivalent ordering.
- [ ] CombatEncounter serializable.
- [ ] six body parts.
- [ ] injury severity/bleeding/impairment.
- [ ] attack/movement/perception Gu.
- [ ] preparation/activation/perception/reaction/resolution.
- [ ] reaction can change outcome.
- [ ] flee/disengage.
- [ ] injury changes later actions.
- [ ] NPC combat decision uses perceived state.
- [ ] mid-combat save/resume deterministic.

## I. Information / Rumor / Belief

- [ ] Observation incomplete/rule-gated.
- [ ] Evidence + support/contradiction.
- [ ] structured Hypothesis.
- [ ] claimed vs actual report basis.
- [ ] deliberate lie does not mutate WorldTruth.
- [ ] source credibility operational.
- [ ] origin chain.
- [ ] independence group.
- [ ] same-origin correlation discount.
- [ ] rumor mutation changes interpreted belief.
- [ ] delayed channels.
- [ ] BeliefStore per NPC.
- [ ] belief decay.
- [ ] MemoryRecord.
- [ ] directional multidimensional Relationship.
- [ ] investigation produces evidence, not truth reveal.
- [ ] absent NPC does not know before delivery.
- [ ] pending transmissions save/resume.

## J. Factions / Politics

- [ ] 3–5 factions/organizations.
- [ ] memberships.
- [ ] offices and authority.
- [ ] political blocs.
- [ ] FactionNeeds.
- [ ] institutional beliefs from delivered info.
- [ ] SocialIdentity / alias minimum.
- [ ] audience-specific ReputationVector.
- [ ] official FactionStanding separate.
- [ ] FactionCase state machine.
- [ ] cases can be disputed/closed.
- [ ] proposal model.
- [ ] governance/voting.
- [ ] office-holder disagreement.
- [ ] influence vector.
- [ ] recruitment/affiliation.
- [ ] sanctions/watch/access changes.
- [ ] faction-generated missions.
- [ ] NPC institutional actions.
- [ ] 48h idle institutional evolution.
- [ ] same event can create cross-faction disagreement.

## K. Missions / Access

- [ ] at least two mission types.
- [ ] AVAILABLE→ACCEPTED→IN_PROGRESS→terminal lifecycle.
- [ ] mission progress uses ordinary world actions.
- [ ] player can ignore mission.
- [ ] ignored mission may expire/reassign/NPC-complete.
- [ ] membership/standing changes real access.
- [ ] contribution/favor exists without becoming XP.

## L. World / Map / LOD

- [ ] hierarchical location graph.
- [ ] 20–40 important local locations target.
- [ ] main settlement.
- [ ] 2–4 smaller settlements/powers.
- [ ] resource areas.
- [ ] trade routes.
- [ ] hidden/optional location.
- [ ] ACTIVE/NEAR/REGIONAL/ABSTRACT simulation levels.
- [ ] remote actors use coarse simulation.
- [ ] active combat uses fine timing.

## M. NPC Autonomy

- [ ] important NPC goals/needs persist.
- [ ] NPCs act while player idles.
- [ ] NPCs cultivate/trade/gather/socially react.
- [ ] NPCs can participate in faction missions.
- [ ] NPCs can investigate.
- [ ] NPCs can fight/flee.
- [ ] NPCs can hold wrong beliefs.
- [ ] at least two NPC future goals differ across final strategies.
- [ ] no “plot wants this” hardcoded decision dependency.

## N. Canon / Provenance

- [ ] CANON_EXPLICIT/FAN_COMPILED/GAME_EXTENSION preserved.
- [ ] unsupported placeholders labeled GAME_EXTENSION.
- [ ] no bulk copyrighted novel text.
- [ ] Canon timeline scaffold exists.
- [ ] canon anchor has preconditions/divergence status.
- [ ] canon anchor does not force impossible events.

## O. Integrated Day 1–10

- [ ] Day1–2 living sandbox.
- [ ] Day3 resource pressure.
- [ ] Day4 combat possibility.
- [ ] Day5 information/social consequences.
- [ ] Day6 breakthrough opportunity.
- [ ] Day7 faction attention.
- [ ] Day8 shortage crisis.
- [ ] Day9 macro player influence.
- [ ] Day10 shipment/caravan consequence.
- [ ] days are systemic windows, not forced quest chapters.

## P. Strategy Divergence

Same seed, cooperative vs adversarial:

- [ ] wealth differs.
- [ ] cultivation/breakthrough differs.
- [ ] Gu condition/feeding differs.
- [ ] killer-move state differs.
- [ ] 3+ NPC relationships differ.
- [ ] 2+ NPC goals differ.
- [ ] NPC injury/survival differs.
- [ ] 2+ market states differ.
- [ ] 2+ resource node states differ.
- [ ] shipment/caravan differs.
- [ ] rumor/belief chain differs.
- [ ] faction case differs.
- [ ] 2+ faction standing/reputation states differ.
- [ ] mission/membership/access differs.
- [ ] future faction goal/proposal differs.
- [ ] event log causally explains divergence.

## Q. CLI / Debug / Documentation

- [ ] V0.1 cooperative CLI.
- [ ] V0.1 adversarial CLI.
- [ ] world summary.
- [ ] market summary.
- [ ] faction summary.
- [ ] rumor/case summary.
- [ ] cultivation summary.
- [ ] killer-move summary.
- [ ] architecture docs current.
- [ ] event catalog current.
- [ ] save schema current.
- [ ] README current.
- [ ] CODEX_REPORT honest about verification levels.

## R. Final Gate

- [ ] implementation committed.
- [ ] pushed.
- [ ] final CI success.
- [ ] remote verified.
- [ ] last_codex_commit points to final code-bearing commit.
- [ ] Gate HEAD handled per GATE_SHA_PROTOCOL.
- [ ] status WAITING_FOR_MASTER.
- [ ] next_actor chatgpt.
- [ ] STOP.

## S. Playable Layer Extension

- [x] PlayerCharacter creation supports 散修 and 家族弟子.
- [x] Starter state is Rank 1, 30 primeval essence, 20 yuan stones and 月光蛊.
- [x] Three daily action points and morning/afternoon/night phases.
- [x] Cultivate, explore, gather, trade and rest actions.
- [x] World Tick updates weather, resources, economy, NPC routines and events.
- [x] Dynamic events retain complete pending choice context across Save/Load.
- [x] Event consequences use serializable target/attribute/change/reason Effects.
- [x] NPC identity, role, goal, wealth, memory and relationship state persists.
- [x] Four-location Qing Mao Mountain outer map is exposed.
- [x] 30-day same-seed demo and Save/Resume regression pass.
- [x] Network/server/realtime/multiplayer namespaces are reserved without moving rule authority.
