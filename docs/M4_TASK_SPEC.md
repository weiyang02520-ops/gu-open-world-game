# M4 Task Spec — Factions, Reputation, Cases and Institutional Politics

> Execution mode: LARGE TASK MODE
> Reviewed M3 repair Gate: `6d291afba23907768725ce9136414b673bdb3533`

## Product question

Can the local world react to the player through institutions rather than a global reputation switch?

M4 must prove this chain:

```text
individual observations / reports / beliefs
→ institutional information
→ faction needs / interests
→ case or proposal
→ office holders / blocs evaluate
→ governance decision
→ standing / mission / sanction / recruitment
→ NPC and player opportunities change
```

A faction must not know WorldTruth automatically.

The same underlying event must be able to produce:

- one NPC's personal opinion;
- local public/audience reputation;
- a faction's institutional belief;
- an official faction action;

and those four states may disagree.

---

# 1. M3 hardening carried into M4

Before building institutional behavior, repair these two non-blocking M3 semantics with tests.

## 1.1 Contradictory evidence must penalize only actually contradicted sources

Current M3 source-credibility feedback walks reports attached to a belief too broadly.

Required:

- when new evidence contradicts a hypothesis, inspect each prior report claim;
- reduce source credibility only when that report's claim conflicts with the evidence-supported interpretation;
- do not penalize a sender whose earlier report is corroborated by the new evidence;
- keep updates evaluator-local;
- add positive and negative tests.

## 1.2 Relationship trust must not increase unconditionally for every report

Current report delivery adds a fixed receiver→sender trust delta.

Required:

- report arrival alone may create/update contact metadata, but trust change must depend on deterministic credibility and/or later validation;
- high-credibility corroborated reporting may increase trust;
- discovered falsehood/strong contradiction may decrease trust;
- low-confidence gossip should not automatically make the receiver trust the sender more;
- preserve directional relationship semantics.

These repairs remain M3-domain code but are authorized inside M4 because M4 depends on them.

---

# 2. Faction model

Introduce FactionDefinition / FactionState or equivalent.

Minimum FactionDefinition fields:

- faction_id;
- name;
- faction_type;
- headquarters_location_id;
- governance_model;
- provenance.

Minimum FactionState fields:

- treasury / liquid resources minimum;
- controlled_locations;
- resource interests / claims;
- security level;
- stability;
- cohesion;
- prestige;
- current needs;
- goals;
- memberships;
- offices;
- blocs;
- institutional beliefs;
- active cases;
- active proposals;
- active missions;
- external relations minimum.

All placeholder local factions are GAME_EXTENSION.

M4 should create at least **3 local factions/organizations** suitable for the current small Southern Border sandbox.

Do not require canonical clan names yet.

---

# 3. Membership

Introduce directional membership state.

Statuses should support at least:

- OUTSIDER
- AFFILIATE
- MEMBER
- INNER_MEMBER
- ELDER or OFFICER
- SUSPENDED
- EXILED
- TRAITOR

M4 does not need every status used in the smoke scenario, but the schema should not collapse membership into one boolean.

Membership record should support:

- character_id;
- faction_id;
- status;
- joined_at;
- contribution / service score;
- loyalty;
- privileges;
- restrictions;
- sponsor / recommender where useful.

Important:

loyalty != official membership != personal relationship.

---

# 4. Offices and authority

Introduce OfficeDefinition / OfficeAssignment.

Minimum examples:

- LEADER
- ELDER / COUNCIL_MEMBER
- STEWARD / QUARTERMASTER
- SECURITY_OFFICER

Office determines authority such as:

- propose recruitment;
- open/close case;
- spend treasury;
- issue mission;
- change official standing;
- vote on proposal.

Do not let every member perform every institutional action.

---

# 5. Political blocs / internal interests

Introduce a simplified PoliticalBloc.

Each major faction in the M4 scenario should have at least two distinguishable interest blocs, for example:

- SECURITY_HARDLINERS
- TRADE_PRAGMATISTS
- CONSERVATIVE_ELDERS
- EXPANSIONISTS

Do not hard-code these names if a cleaner generic model is better.

Bloc state should include:

- bloc_id;
- faction_id;
- members / office holders;
- priorities;
- influence;
- preferred policies;
- risk tolerance.

M4 only needs simplified internal politics, not a complete parliament simulator.

---

# 6. Faction needs

Introduce FactionNeed / institutional pressure.

At minimum support:

- SECURITY
- RESOURCES
- REVENUE
- STABILITY
- PRESTIGE
- INTELLIGENCE
- RECRUITMENT / MANPOWER

Need intensity must be stateful and deterministic.

Faction needs should influence proposals/missions.

Example:

high SECURITY need
→ investigation/guarding proposal becomes more attractive.

high RESOURCE need
→ procurement/recruitment/trade mission becomes more attractive.

Do not make needs mere labels with no decision effect.

---

# 7. Institutional information boundary

Hard requirement.

A faction does not read the global event log as truth.

Institutional knowledge must come from:

- member reports;
- authorized investigations;
- official notices;
- trusted external reports;
- records.

Introduce FactionInstitutionalBelief or equivalent, derived from M3 information structures.

Institutional belief should track:

- faction_id;
- hypothesis_id;
- confidence;
- source reports/evidence;
- origin groups;
- updated_at;
- official_status / adopted or disputed state.

Different officers may hold different personal beliefs even when the institution has an official position.

Required test:

- an absent faction cannot open a confirmed case merely because a hidden event exists;
- it reacts only after information reaches an authorized member/channel.

---

# 8. Identity and audience

Introduce a minimal SocialIdentity layer or equivalent.

The player/NPC may have:

- real character identity;
- public/known alias;
- faction-known identity;
- optional concealed/unknown identity.

M4 does not need a full disguise simulator.

Purpose:

reputation and cases should attach to the identity the audience believes responsible.

Required:

- a report may refer to an alias/unknown actor;
- faction standing should not automatically transfer from alias to real identity unless linkage becomes known.

---

# 9. Reputation vector

Do not use one reputation integer.

Introduce audience-scoped ReputationVector.

At minimum dimensions:

- trust;
- competence;
- strength;
- danger;
- reliability;
- generosity;
- ruthlessness;
- unpredictability.

M4 smoke need not exercise all dimensions equally, but the data model should preserve them independently.

Reputation is:

```text
audience + identity -> ReputationVector
```

Possible audiences:

- a faction;
- local market participants;
- settlement public;
- a subgroup/bloc.

Reputation changes must come from information believed by that audience, not direct WorldTruth.

---

# 10. Official faction standing

Keep official standing separate from reputation.

Support at least:

- UNKNOWN
- NEUTRAL
- TOLERATED
- FRIENDLY
- GUEST
- ALLY
- MEMBER
- SUSPICIOUS
- WATCHED
- WANTED
- HOSTILE
- ENEMY

Standing is institutional policy.

Examples:

- public thinks player is dangerous, but faction is still NEUTRAL;
- one elder respects player, but faction officially WATCHES them;
- faction considers player FRIENDLY even while a trader personally dislikes them.

Standing changes require authorized institutional action/proposal.

No instant global aggro switch.

---

# 11. Faction cases

Introduce FactionCase.

Status minimum:

- RUMOR
- UNDER_INVESTIGATION
- SUSPECTED
- CONFIRMED
- DISPUTED
- CLOSED

Case fields should cover:

- case_id;
- faction_id;
- subject identity;
- relevant hypotheses;
- opened_at;
- status;
- evidence/report references;
- assigned investigator;
- institutional confidence;
- recommended actions;
- history.

Hard rule:

```text
crime / rumor != confirmed guilt
```

A case may remain disputed indefinitely.

False reports can create a case.
Independent contradictory evidence can weaken/close it.

---

# 12. Investigation integration

Reuse M3 evidence/observation architecture.

Institutional investigation may:

- assign investigator;
- inspect scene;
- question witness;
- compare reports;
- request records.

It must not reveal WorldTruth directly.

Investigation output:

- new Observation;
- new Evidence;
- new Report;
- institutional belief update;
- case history event.

M4 may wrap M3 investigation with faction authority/cost/time.

---

# 13. Proposals

Introduce FactionProposal.

Proposal types should include at least:

- OPEN_INVESTIGATION
- WATCH_SUBJECT
- RECRUIT_SUBJECT
- OFFER_AFFILIATION
- ISSUE_MISSION
- REWARD_SUBJECT
- RESTRICT_ACCESS
- SANCTION_SUBJECT
- CLOSE_CASE

Optional:
- TREASURY_SPEND
- RESOURCE_PROCUREMENT

Proposal fields:

- proposal_id;
- faction_id;
- type;
- proposer;
- target;
- created_at;
- rationale / referenced needs;
- referenced beliefs/cases;
- cost;
- risks;
- votes/evaluations;
- status;
- resolution.

No LLM decides proposal legality/outcome.

---

# 14. Governance

Implement a deterministic simplified governance model.

At minimum support:

- leader-decides;
- council-majority or weighted council.

At least one M4 scenario faction must use multiple office holders whose evaluations can disagree.

Evaluation inputs:

- personal belief from M3;
- institutional belief;
- relationship to subject;
- bloc priorities;
- faction needs;
- cost;
- risk;
- political gain/loss.

Provide a documented GAME_EXTENSION utility formula or equivalent.

Required proof:

Two office holders can vote differently on the same proposal for explainable reasons.

---

# 15. Influence

Introduce minimal political InfluenceVector or equivalent.

At least:

- formal authority;
- economic influence;
- information influence;
- prestige;
- coercive/military influence.

Do not reduce all internal politics to office rank.

Influence affects proposal resolution where governance model permits.

---

# 16. Faction missions

Faction Mission is a world opportunity, not a forced main quest.

Mission fields:

- mission_id;
- faction_id;
- issuer;
- related faction need/proposal;
- objective type;
- target/location;
- reward/resource promise;
- deadline;
- eligibility;
- status.

Support at least:

- INVESTIGATE
- GATHER / SUPPLY
- ESCORT / GUARD placeholder if no caravan yet
- DELIVER_MESSAGE
- RECRUIT / CONTACT
- WATCH_TARGET

Do not implement M5 shipment/caravan logistics yet.

Player can ignore a mission.
Ignoring it does not freeze faction activity.

NPCs may also receive/perform missions in simplified form.

---

# 17. Faction response to M3 information

Required integrated behavior:

1. an M2/M3 incident occurs;
2. one faction receives incomplete information;
3. a personal NPC reaction occurs;
4. institutional belief is updated;
5. a case or proposal is created;
6. internal office/bloc disagreement occurs;
7. governance resolves an official action;
8. official standing / mission / watch state changes;
9. later independent evidence can alter the case or proposal.

This must be event-driven and deterministic.

---

# 18. Individual vs audience vs institution vs official policy

Hard acceptance test.

For one subject, show all four simultaneously:

- NPC personal relationship/belief;
- public or market ReputationVector;
- FactionInstitutionalBelief;
- official FactionStanding.

They must be stored separately and may disagree.

No shared scalar may silently stand in for all four.

---

# 19. Required M4 scenarios

## Scenario A — rumor creates investigation, not instant hostility

- player is implicated by an M3 report/rumor;
- faction receives information through an authorized path;
- case opens as RUMOR or UNDER_INVESTIGATION;
- official standing becomes at most SUSPICIOUS/WATCHED;
- faction does not instantly become HOSTILE/WANTED without sufficient evidence.

## Scenario B — council disagreement

- proposal: recruit, watch, sanction, or close case;
- two office holders / blocs evaluate differently;
- deterministic governance resolves the proposal;
- event log explains votes and reasons.

## Scenario C — exoneration / dispute

- independent evidence contradicts the initial accusation;
- institutional confidence changes;
- case can move CONFIRMED/SUSPECTED → DISPUTED/CLOSED or similar;
- source credibility changes only for actors who receive the correcting information;
- official standing may improve.

## Scenario D — mission from faction need

- faction need is high;
- proposal or rule creates a mission;
- player can accept or ignore;
- NPC may execute an equivalent mission path;
- the mission exists because of faction state, not a scripted story trigger.

---

# 20. Membership / recruitment scenario

At least one path should allow:

```text
outsider
→ observed useful behavior / reputation
→ recruit proposal
→ governance approval
→ AFFILIATE or MEMBER
```

and another path from the same baseline should allow:

```text
outsider
→ suspicious information
→ WATCHED / case
→ recruitment withheld
```

This is not a mandatory player progression path.

---

# 21. Save/Resume and determinism

Persist:

- factions;
- memberships;
- offices;
- blocs;
- needs;
- institutional beliefs;
- reputations;
- identities;
- standings;
- cases;
- proposals/votes;
- missions;
- external relations minimum.

Required:

same seed + same information/actions
→ identical faction state, proposal results and ordered events.

Save while:

- case is open;
- proposal is pending;
- mission exists;

reload and continue
→ same result as uninterrupted simulation.

---

# 22. Durable events

Add structured equivalents of:

- FACTION_INFORMATION_RECEIVED
- INSTITUTIONAL_BELIEF_UPDATED
- REPUTATION_CHANGED
- FACTION_STANDING_CHANGED
- CASE_OPENED
- CASE_STATUS_CHANGED
- INVESTIGATOR_ASSIGNED
- FACTION_PROPOSAL_CREATED
- FACTION_VOTE_CAST
- FACTION_PROPOSAL_RESOLVED
- MEMBERSHIP_CHANGED
- OFFICE_ASSIGNED
- MISSION_CREATED
- MISSION_ACCEPTED
- MISSION_COMPLETED / FAILED where demonstrated
- FACTION_NEED_CHANGED

Exact names may differ if documented.

Use the one authoritative WorldState event log.

---

# 23. M1/M2/M3 regression

All previous tests and smoke scenarios remain passing.

Keep:

- M1 economy/cultivation/Gu loop;
- M2 combat/reaction/save-resume;
- M3 truth/information separation;
- rumor mutation;
- correlated-source discount;
- directional relationships;
- credibility tests;
- same-time combat ordering.

Do not let M4 institutional convenience bypass M3 beliefs.

---

# 24. CI

CI should run:

1. install;
2. full pytest;
3. M1 smoke;
4. M2 smoke;
5. M3 smoke;
6. M4 faction smoke.

Keep runtime reasonable.

---

# 25. Documentation

Add/update:

- M4 architecture;
- faction model;
- identity/reputation/standing separation;
- institutional belief boundary;
- case state machine;
- proposal/governance formula;
- bloc/influence model;
- membership/offices;
- mission generation;
- M4 CLI scenario;
- AGENT_MEMORY;
- CHATGPT_MEMORY;
- HANDOFF;
- CODEX_REPORT.

---

# 26. Explicitly out of scope

Do not implement:

- M5 full resource-crisis/logistics/caravan system;
- large-scale warfare;
- full territory conquest;
- nation-level diplomacy;
- M6 attainment/breakthrough expansion;
- M7 Effect Graph;
- graphical faction UI;
- natural-language LLM council debates;
- Gu Immortal sect politics.

---

# 27. PASS criteria

M4 PASS requires:

- M3 hardening items in section 1 fixed and tested.
- At least 3 local factions/organizations exist.
- Membership and office authority are separate.
- At least one faction has 2+ political blocs/interests.
- FactionNeeds materially affect proposals/missions.
- Institutional beliefs derive from delivered information, not hidden truth.
- Reputation is multidimensional and audience-specific.
- Official standing is separate from reputation.
- Cases support rumor/investigation/suspected/confirmed/disputed/closed semantics.
- False information can open a case without creating instant confirmed guilt.
- Authorized investigation uses M3 evidence, not truth reveal.
- Proposal/governance system produces deterministic resolution.
- Two office holders/blocs can disagree for explainable reasons.
- Recruitment/watch/sanction/close-case or equivalent official actions are supported.
- At least one mission is generated from faction state/need.
- Player can ignore a mission without freezing faction operation.
- Individual opinion, audience reputation, institutional belief and official standing can disagree simultaneously.
- Correcting evidence can alter a case and official response.
- Save/Resume of open case + pending proposal/mission is deterministic.
- M1/M2/M3 regressions pass.
- CI install/test/M1/M2/M3/M4 smoke passes.
- all new tuning values are GAME_EXTENSION.
- no M5+ scope creep.
- docs/Memory/Handoff/CODEX_REPORT updated.
- last_codex_commit follows `docs/GATE_SHA_PROTOCOL.md`.
- status = WAITING_FOR_MASTER / next_actor=chatgpt.
- STOP before M5.

## Quality bar

M4 fails if the social system is effectively:

```text
player did bad thing
→ faction reputation -10
→ guards hostile
```

M4 passes when:

```text
someone reports an incident
→ different people believe different versions
→ institution receives only some information
→ case opens
→ office holders disagree
→ faction need/bloc interest affects proposal
→ governance creates an official policy
→ later evidence can reverse or dispute it
```

with the event log explaining every institutional step.
