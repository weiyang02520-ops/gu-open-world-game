# M3 Task Spec — Information, Memory, Relationships and Rumor

> Execution mode: LARGE TASK MODE
> Reviewed M2 baseline: `60b4b776ef18c5992ceb6b7ed3131feac7f17469`

## Product question

Can the world stop being omniscient?

M3 must prove that a real World Event can be observed imperfectly, converted into evidence/reports, spread through rumor, remembered differently by different NPCs, and produce different decisions because NPCs hold different beliefs.

The required chain is:

```text
World Event
→ Observation
→ Evidence
→ Report
→ Rumor
→ Belief
→ Memory / Relationship
→ Decision under incomplete information
→ New World Event
```

M3 is complete only when the same underlying event can lead two NPCs to materially different conclusions and behavior.

---

# 1. Core architecture boundary

WorldState remains authoritative truth.

NPC decision code must not automatically read hidden truth when deciding about past/off-screen events.

Introduce a serializable M3 information state under WorldState.game_state or an equivalent versioned domain boundary.

Conceptually include:

- observations;
- evidence;
- hypotheses;
- reports;
- rumor threads;
- source profiles;
- per-character belief stores;
- per-character memories;
- relationships;
- scheduled information transmissions;
- minimal investigations.

All durable state must save/load deterministically.

---

# 2. Hypotheses

Introduce stable structured hypotheses.

Conceptual model:

```text
Hypothesis
- hypothesis_id
- subject_id
- predicate
- object_id / structured value
- parameters
```

Examples:

- player attacked NPC-A;
- player is dangerous;
- NPC-B owns a certain resource;
- an unknown third party caused an injury.

Do not store beliefs only as free-text strings.

Different mutually incompatible hypotheses must be able to coexist.

---

# 3. Observation

An NPC may only form a direct observation when a rule says the event was perceivable.

Observation should include at least:

- observation_id;
- observer_id;
- event_id where applicable;
- location_id;
- observed_at;
- observation_type;
- perceived features;
- perception quality;
- confidence;
- source visibility/sensory basis;
- generated evidence IDs where relevant.

M3 must integrate with at least M2 combat events.

Examples:

- witness saw player and NPC fighting;
- witness saw a wounded NPC leave;
- witness heard a Gu activation but did not identify the attacker.

The observation may be incomplete or wrong.

Do not simply copy the complete DomainEvent payload into every observer.

---

# 4. M2 perceived-state hardening

M2 PASS note:

`PerceivedCombatSnapshot.target_movement_impairment` is currently derived directly from the true target body state.

For active close combat this was accepted as a visible signal.

M3 must formalize the rule:

- hidden exact injury dictionaries remain private;
- perceived impairment should be exposed as a visible/estimated signal, preferably coarse or confidence-tagged;
- off-screen/social decisions must use M3 Observation/Belief rather than direct body-state reads;
- active combat may still use immediate perceptual snapshots where explicitly justified.

Add a regression proving hidden exact target injury/essence data does not leak into persistent beliefs.

---

# 5. Evidence

Introduce EvidenceItem with at least:

- evidence_id;
- evidence_type;
- origin_event_id / origin_observation_id;
- location / holder;
- created/discovered time;
- quality;
- authenticity;
- tampered flag;
- independence_group_id;
- related hypothesis support.

Evidence types for M3 may be limited but should include several concrete classes such as:

- witness testimony;
- wound pattern / injury observation;
- dropped object / trace;
- trade record or other structured record;
- generic physical trace.

Do not require a full forensic simulator.

Important distinction:

- authenticity: is the evidence itself genuine?
- support strength: how strongly does it support one hypothesis?

One evidence item may support multiple hypotheses at different strengths.

---

# 6. Evidence support / contradiction

Represent evidence-to-hypothesis relation explicitly.

Conceptually:

```text
EvidenceSupport
- evidence_id
- hypothesis_id
- support_strength
- contradiction_strength
- evaluator / interpretation context if needed
```

This allows a genuine clue to weakly support one explanation and strongly contradict another.

All numeric combination rules are GAME_EXTENSION.

---

# 7. Report

Introduce structured InformationReport.

Required fields should cover:

- report_id;
- sender_id;
- receiver_id or audience;
- created_at;
- source_type/channel;
- reported claims;
- claimed basis;
- actual internal basis;
- asserted confidence;
- evidence references;
- intention;
- transmission quality;
- parent_report_id;
- origin_chain_id;
- independence_group_id.

Minimum intentions:

- INFORM
- WARN
- PERSUADE
- DECEIVE
- FRAME

M3 must support deliberate false reporting.

A lie must not mutate WorldTruth.

---

# 8. Claimed basis vs actual basis

Required distinction.

A report may claim:

> “I saw it myself.”

while actual_basis is SECOND_HAND or DELIBERATE_LIE.

Persist both internally.

Receivers must not automatically know actual_basis.

Only later investigation/evidence may expose the discrepancy.

---

# 9. Source profile / credibility

Per evaluator-source pair or equivalent, support:

- trustworthiness;
- domain expertise;
- honesty history;
- relationship bias;
- known motive modifiers;
- last updated.

Report credibility should combine a documented deterministic GAME_EXTENSION rule using factors such as:

- source trust;
- claimed confidence;
- basis type;
- transmission quality;
- relationship;
- motive;
- corroboration.

Do not use LLM judgment for numeric belief updates.

---

# 10. Correlated sources

Hard requirement.

Every report/evidence chain must carry enough lineage to avoid:

```text
one rumor repeated by five people
= five independent confirmations
```

Use:

- origin_chain_id;
- independence_group_id;
- belief-store origin groups already counted.

Belief update must heavily discount repeated correlated reports.

Required test:

- first rumor raises confidence;
- four repeated retellings from the same origin do NOT raise confidence as much as two independent corroborating observations.

---

# 11. Belief store

Per NPC, introduce structured BeliefRecord.

At minimum:

- hypothesis_id;
- confidence;
- supporting evidence IDs;
- contradicting evidence IDs;
- report IDs;
- origin groups seen;
- last_updated;
- certainty class;
- freshness / decay metadata where applicable.

Suggested visible certainty classes:

- VERY_UNLIKELY
- UNLIKELY
- POSSIBLE
- LIKELY
- VERY_LIKELY
- NEAR_CERTAIN

Thresholds are GAME_EXTENSION.

Do not require full Bayesian networks in M3.

A deterministic simplified odds/confidence update is acceptable if documented and tested.

---

# 12. Belief decay / freshness

Not all beliefs decay equally.

M3 minimum:

- current location / immediate activity beliefs decay relatively fast;
- major witnessed violence or strong personal memory decays slowly;
- ordinary rumor confidence can decay if not refreshed.

Implement a simple category-based deterministic decay policy.

Do not delete important memories just because confidence decayed.

---

# 13. Memory

Introduce per-character MemoryRecord or equivalent.

Memory should preserve significant experienced information separately from current numeric belief confidence.

Fields should include enough to represent:

- memory_id;
- character_id;
- event/observation/report references;
- memory type;
- salience;
- emotional tags;
- created_at;
- last_recalled;
- persistence/decay.

Minimum emotional tags may include:

- FEAR
- ANGER
- GRATITUDE
- HUMILIATION
- CURIOSITY

M3 does not need a psychology simulator.

Required integration:

A witnessed attack against the NPC or ally should create a more salient memory than generic market gossip.

---

# 14. Relationships

Do not use a single friendship number.

Introduce a minimal multidimensional relationship state between characters.

At least support:

- trust;
- fear;
- respect;
- resentment;
- debt/favor if useful.

Relationship changes must come from events/beliefs/memories.

Examples:

- witnessed aid → trust/respect;
- credible betrayal report → trust down;
- believed dangerous opponent → fear up;
- repeated unreliable reports → source trust down.

Do not implement faction reputation here.

---

# 15. Rumor thread

Introduce RumorThread with enough state for:

- primary hypothesis;
- origin report / origin chain;
- created_at;
- origin location;
- current locations / audiences;
- spread strength;
- mutation level;
- public visibility;
- active/expired status.

Rumor content must remain structured.

LLM prose rendering is out of scope.

---

# 16. Information channels / scheduler

Support at least several deterministic channels, e.g.:

- FACE_TO_FACE
- MARKET_GOSSIP
- MESSENGER
- LOCAL_NETWORK

Each channel may have GAME_EXTENSION:

- delivery delay;
- reliability;
- distortion;
- reach;
- interception exposure if desired.

Use the existing scheduler/world time or add a compatible deterministic transmission queue.

Required:

A report sent through a delayed channel must arrive later in WorldClock time, not instantly.

Save/resume while transmissions are pending must reproduce the same delivery order/outcome.

---

# 17. Rumor mutation

M3 should support limited structured mutation, not generated prose.

For example slots:

- actor;
- action;
- target;
- location;
- severity.

A retelling may:

- preserve;
- omit;
- exaggerate;
- replace unknown with guessed actor;

according to deterministic seeded GAME_EXTENSION rules.

Required test:

At least one multi-hop rumor changes one semantic slot while preserving its origin chain.

---

# 18. Minimal investigation

Add a bounded investigation layer sufficient to create new observations/evidence.

Conceptual actions:

- INSPECT_SCENE
- QUESTION_WITNESS
- COMPARE_REPORTS

An InvestigationTask may hold:

- investigator;
- target hypotheses;
- known evidence;
- search location;
- budget/time;
- status.

M3 does not implement faction cases.

Investigation must NOT call a “reveal truth” function.

It generates evidence/observations that update beliefs.

---

# 19. NPC information actions

Extend NPC behavior with a minimal information decision layer.

NPCs should be able to choose contextually among actions equivalent to:

- TELL
- WARN
- KEEP_SECRET
- ASK
- INVESTIGATE
- AVOID_TARGET
- APPROACH_TARGET

Do not build the final full GOAP system.

Decision inputs:

- current goals/needs from M1;
- relationship;
- belief confidence;
- memory salience;
- information value;
- risk.

Required proof:

Two NPCs who know different things about the same player choose different behavior.

---

# 20. Decision under uncertainty

At least one NPC decision must evaluate a belief rather than authoritative truth.

Example scenario:

WorldTruth:
- player defeated attacker in self-defense.

NPC A:
- direct witness, confidence high that player acted defensively.

NPC B:
- receives distorted rumor saying player attacked first.

Expected:
- NPC A approaches / remains neutral / warns accurately.
- NPC B avoids player or warns others.

Both decisions must be explainable from their BeliefStore.

---

# 21. Required integrated scenario

Provide an M3 smoke scenario built on M1/M2.

Suggested structure:

1. Player and NPC-A have a combat encounter.
2. Witness NPC-B directly observes enough to form one hypothesis.
3. NPC-C is absent and receives a second-hand report.
4. A retelling reaches NPC-D through gossip.
5. At least one report is deliberately false or distorted.
6. Two NPCs end with different confidence values about who initiated the violence / how dangerous the player is.
7. Their relationship or behavior toward the player differs.
8. One investigation/independent observation can partially correct a false belief.

The exact story can differ, but it must be systemic and deterministic.

---

# 22. Required event types

Add structured equivalents where appropriate:

- OBSERVATION_CREATED
- EVIDENCE_DISCOVERED
- REPORT_CREATED
- REPORT_DELIVERED
- RUMOR_CREATED
- RUMOR_SPREAD
- RUMOR_MUTATED
- BELIEF_UPDATED
- MEMORY_FORMED
- RELATIONSHIP_CHANGED
- INVESTIGATION_STARTED
- INVESTIGATION_RESULT
- INFORMATION_ACTION_SELECTED

Exact names may differ if documented consistently.

All use the authoritative durable event log.

---

# 23. Determinism / save-resume

M3 must prove:

- same seed + same events/actions → same observations/reports/rumor mutations/beliefs;
- pending information transmission survives save/load;
- resumed run equals uninterrupted run;
- origin_chain / independence_group lineage survives save/load;
- memory and relationships survive save/load.

No wall clock.
No unseeded randomness.

---

# 24. M2 regression requirements

Keep M1 and M2 passing.

Add a dedicated test for equal-time combat action ordering:

- two actions have the same execute_at_ms;
- deterministic sequence decides resolution order;
- save/load does not change that order.

This was a non-blocking M2 review note and becomes required regression coverage in M3.

Also preserve:

- M1 Day 1–2 smoke;
- M2 combat smoke;
- M1 save compatibility;
- M2 active-combat resume.

---

# 25. Information privacy tests

Required negative tests:

1. NPC belief does not contain exact hidden player essence unless actually observed/reported by an allowed rule.
2. NPC belief does not directly copy the target's internal injury dictionary.
3. An absent NPC does not know a combat event before a report/rumor reaches them.
4. A false report does not mutate WorldTruth.
5. Repeated same-origin reports are discounted.

---

# 26. CI

CI should run:

1. install;
2. full pytest;
3. M1 smoke;
4. M2 smoke;
5. M3 information/rumor smoke.

Keep runtime reasonable.

---

# 27. Documentation

Add/update:

- M3 architecture;
- truth vs information boundary;
- observation rules;
- evidence/hypothesis model;
- report lineage;
- belief update formula;
- rumor channels/mutation;
- memory/relationship model;
- investigation boundary;
- M3 CLI scenario;
- AGENT_MEMORY;
- CHATGPT_MEMORY;
- HANDOFF;
- CODEX_REPORT.

---

# 28. Explicitly out of scope

Do not implement:

- faction institutional beliefs / cases / politics;
- faction reputation/official standing;
- large-scale law enforcement;
- M5 caravans/resource crisis expansion;
- M6 attainment/breakthrough expansion;
- M7 Effect Graph/killer-move editor;
- graphical dialogue UI;
- LLM-generated rumor truth;
- full natural-language social simulation.

These belong later.

---

# 29. PASS criteria

M3 PASS requires all of the following:

- M1 and M2 regressions pass.
- Equal-time combat ordering receives explicit deterministic regression coverage.
- WorldTruth and NPC information state are separate.
- Direct observation is rule-gated and incomplete.
- Evidence supports/contradicts structured hypotheses.
- Reports carry claimed basis, actual basis, lineage and intention.
- Deliberate false report is supported without changing truth.
- Correlated retellings are discounted.
- Independent corroboration affects confidence more strongly than repeated same-origin rumor.
- Beliefs are per-NPC and may be wrong.
- Belief freshness/decay works deterministically.
- Significant events form memories.
- Relationship state is multidimensional.
- Rumors spread over time through deterministic channels.
- At least one rumor mutates a structured semantic slot.
- Minimal investigation generates evidence/observation rather than revealing truth.
- At least two NPCs make different decisions because they hold different beliefs.
- Absent NPC does not know an event before information delivery.
- pending transmissions + beliefs + memory + relationships survive save/resume exactly.
- CI install/test/M1-smoke/M2-smoke/M3-smoke passes.
- all new coefficients/thresholds are marked GAME_EXTENSION.
- no M4+ scope creep.
- docs/Memory/Handoff/CODEX_REPORT updated.
- exact final Codex HEAD recorded, pushed and remote-verified.
- CURRENT_STATE ends WAITING_FOR_MASTER / next_actor=chatgpt.
- STOP before M4.

## Quality bar

M3 does not pass if the implementation is only:

```text
event happened
→ every NPC gets reputation -10
```

It passes when:

```text
event happened
→ one NPC saw part of it
→ another heard a distorted retelling
→ one source lied
→ correlated copies were discounted
→ beliefs diverged
→ memories/relationships changed
→ NPCs chose different actions
```

and the event log can explain the full chain.
