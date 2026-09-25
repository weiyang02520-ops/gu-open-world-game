# M3 Repair Spec — Credibility, Relationship Direction and Effective Rumor Mutation

> Task: TASK-M3-FIX-001
> Baseline reviewed Gate: `d13f7e71e5a7fa597c5d54efcc25d385eca54c09`
> Verdict that triggered this repair: CHANGES_REQUESTED

## Why this repair exists

M3 is structurally strong, but several semantic defects would contaminate M4 faction decisions if left unresolved.

This repair is deliberately bounded to M3 semantics. Do not begin M4.

---

# 1. Fix relationship direction

Current behavior in report delivery updates:

`relationship(report.sender_id, receiver_id).trust`

Given the model semantics:

`RelationshipState.source_id -> target_id`

the trust affected by receiving a report should be the **receiver's relationship toward the sender**, not the sender's relationship toward the receiver.

Required:

- change the direction to receiver -> sender where report credibility/trust experience updates relationship;
- audit all M3 relationship writes for the same directional mistake;
- update `last_updated` whenever relationship dimensions change;
- add tests proving sender->receiver and receiver->sender are distinct directional records;
- receiving a credible report changes receiver's trust in sender only.

Do not make relationships symmetric automatically.

---

# 2. Make SourceProfile fields operational

`SourceProfile` currently stores:

- trustworthiness;
- domain_expertise;
- honesty_history;
- relationship_bias;
- motive_modifier.

The belief update must actually use these fields in a documented deterministic credibility rule.

Required:

- introduce a single clear credibility calculation function;
- use claim asserted confidence;
- channel/transmission quality;
- claimed basis;
- trustworthiness;
- domain expertise;
- honesty history;
- relationship bias;
- motive modifier;
- relationship state where appropriate;
- correlated-source penalty remains separate and preserved.

All coefficients are GAME_EXTENSION.

Tests must prove, holding the report constant:

1. higher trustworthiness increases effective belief impact;
2. higher expertise increases effective impact for a relevant report;
3. better honesty history increases effective impact;
4. a negative motive modifier reduces effective impact;
5. relationship trust/bias changes effective impact in the expected direction.

Do not use actual_basis when calculating receiver credibility unless the receiver has legitimately discovered the lie.

---

# 3. Update source credibility from discovered inconsistency

M3 needs at least one minimal feedback hook so credibility can evolve.

Required bounded behavior:

- when an investigation or strong independent evidence contradicts a previously delivered report, the evaluator can reduce its source profile trustworthiness and/or honesty_history;
- do not globally reveal that a sender lied;
- only evaluators who obtained the contradictory evidence should update their source profile;
- emit a structured event such as SOURCE_CREDIBILITY_UPDATED or equivalent;
- persist through save/load.

A full deception-detection system is out of scope.

---

# 4. Make rumor mutation affect interpreted information

Current mutation changes `RumorThread.semantic_slots`, while report claims delivered to Belief remain unchanged.

This makes mutation mostly cosmetic.

Required:

- a mutated retelling must create or deliver an **interpreted/derived claim representation** that corresponds to the mutated semantic slots;
- preserve the original `origin_chain_id` and `independence_group_id`;
- never mutate original WorldTruth;
- never overwrite the original source report in place if doing so destroys provenance;
- preserve parent/derivation linkage;
- correlated-source discount must still recognize the mutated retelling as the same origin unless truly independent.

You may implement this by:
- derived report;
- derived hypothesis;
- report-view / interpreted claim;
- another clean deterministic model.

Required test:

A rumor whose initiator mutates from actor A to "unknown-third-party" must cause the receiver's belief state to reflect the mutated interpretation rather than simply receiving the original actor-A claim unchanged.

---

# 5. Strengthen rumor lineage test

Add an explicit multi-hop test:

```text
source observation/report
→ hop 1
→ hop 2 with mutation
→ hop 3
```

Verify:

- origin_chain_id unchanged;
- independence_group_id unchanged;
- parent lineage preserved;
- mutation level increases;
- belief impact is discounted as correlated;
- semantic interpretation at final receiver reflects the mutation.

---

# 6. Belief category update semantics

Audit `_belief_record`.

Currently a belief first created as RUMOR can later receive direct evidence while keeping its original category.

Required:

- define/document how evidence freshness category is determined after mixed inputs;
- direct independent evidence should not continue to decay as pure rumor merely because rumor arrived first;
- implement a simple deterministic policy such as strongest/current source category;
- add a regression test.

Do not build a Bayesian network.

---

# 7. Investigation boundary

Keep the rule:

investigation does not reveal truth directly.

But strengthen API semantics so callers cannot accidentally use investigation as an unrestricted truth injection.

Required:

- document that evidence support mappings come from registered deterministic investigation rules / trace interpretation, not arbitrary UI/NPC truth knowledge;
- if practical within the repair, route support generation through a rule/helper keyed by observable event/trace type;
- tests should prove investigation creates observation/evidence and then Belief updates from that evidence.

A fully generic forensic engine is out of scope.

---

# 8. Gate bookkeeping

At final completion:

- push implementation;
- run CI;
- create final Gate state;
- push final Gate commit;
- remote-verify exact final `origin/main` SHA;
- `.ai/CURRENT_STATE.json.last_codex_commit` MUST equal that exact final Gate SHA, not the preceding implementation SHA;
- CODEX_REPORT must list both implementation SHA and final Gate SHA;
- status = WAITING_FOR_MASTER;
- next_actor = chatgpt.

If updating CURRENT_STATE changes the commit SHA, use a workflow that can truthfully record the final state without a self-referential impossible value. If exact self-SHA storage is structurally impossible in a commit that contains itself, document this clearly and redefine the field semantics in the protocol rather than repeatedly claiming an impossible invariant. Prefer a separate remote-verification record if needed.

This point must be explicitly resolved rather than silently repeated.

---

# 9. Required regression suite

All prior tests must still pass.

Add tests for:

- directional relationship update;
- SourceProfile factor sensitivity;
- source credibility update after contradiction;
- rumor mutation affects receiver interpretation;
- multi-hop lineage preservation;
- mixed rumor + direct evidence category/decay behavior;
- M1/M2/M3 Save/Resume unchanged;
- same-time combat sequence test retained.

CI must still run M1/M2/M3 smoke.

---

# 10. Scope boundary

Do NOT implement:

- faction institutional beliefs;
- faction cases/politics;
- official reputation/standing;
- M5 logistics;
- M6 attainment;
- M7 Effect Graph;
- UI.

This is an M3 repair only.

---

# 11. PASS criteria

TASK-M3-FIX-001 passes when:

- relationship direction is correct and tested;
- all declared SourceProfile dimensions materially participate in deterministic credibility;
- relationship/source credibility actually influences report belief impact;
- contradictory independent evidence can update only the evaluator's view of source credibility;
- rumor mutation changes the receiver's interpreted belief, not just metadata;
- multi-hop lineage/correlation remains intact;
- mixed direct evidence/rumor decay semantics are documented and tested;
- investigation remains evidence-producing, not truth-revealing;
- all previous tests and smoke scenarios pass;
- save/resume remains deterministic;
- CI passes;
- docs/Memory/Handoff/CODEX_REPORT updated;
- final remote state and Gate bookkeeping semantics are truthful and internally consistent;
- WAITING_FOR_MASTER / next_actor=chatgpt;
- STOP before M4.
