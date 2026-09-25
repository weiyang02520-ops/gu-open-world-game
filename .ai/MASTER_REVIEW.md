# Master Review

## M3 / TASK-M3-001

- Reviewed remote HEAD: `d13f7e71e5a7fa597c5d54efcc25d385eca54c09`
- Verdict: **CHANGES_REQUESTED**
- Reviewer: External ChatGPT Web Master
- Date: 2026-09-25

## What passed

Remote implementation and CI confirm that M3 has a strong structural base:

- WorldTruth is separated from per-NPC information state.
- Observation is incomplete and does not copy hidden essence/injury dictionaries.
- Structured Hypothesis / Evidence / EvidenceSupport / Report / Belief models exist.
- Claimed basis and actual basis are separated.
- False reports do not mutate the underlying World Event.
- origin_chain_id / independence_group_id survive transmission.
- Correlated reports are discounted.
- Belief decay, MemoryRecord, RelationshipState, delayed channels and investigation exist.
- M1/M2 regressions pass.
- Equal-time combat ordering now has explicit regression coverage.
- Pending-transmission Save/Resume is deterministic.
- Final Gate CI passed at `d13f7e71e5a7fa597c5d54efcc25d385eca54c09`.

## Blocking semantic issues

### 1. Relationship direction is reversed during report delivery

The model is directional:

`RelationshipState.source_id -> target_id`

but report delivery currently updates:

`relationship(report.sender_id, receiver_id).trust`

This means receiving a report makes the sender trust the receiver more, instead of changing the receiver's trust in the sender.

This must be corrected and tested before M4.

### 2. SourceProfile fields are mostly inert

SourceProfile stores:

- trustworthiness
- domain_expertise
- honesty_history
- relationship_bias
- motive_modifier

but the actual report belief calculation currently uses only a subset (primarily trustworthiness, channel quality and claimed basis).

M3 explicitly requires credibility to depend on source expertise/history/bias/motive/relationship. These fields must become operational and tested.

### 3. Rumor mutation is currently mostly metadata-only

`RumorThread.semantic_slots` mutates, but the receiver still receives the original report claims.

Therefore a changed initiator/action slot can be visible in rumor metadata while the receiver's BeliefStore still reflects the unmutated semantic claim.

Mutation must affect interpreted information while preserving provenance and correlation lineage.

### 4. Gate SHA invariant is self-referential

The previous task required CURRENT_STATE inside the final commit to contain that same final commit SHA. A Git commit cannot contain its own SHA because changing the file changes the SHA.

The workflow must stop claiming this impossible invariant.

Recommended semantics:

- `last_codex_commit` = final code-bearing implementation commit;
- remote HEAD is resolved externally at review time;
- optional gate verification metadata may refer to the known parent or be stored out-of-band;
- reports must state exactly what was verified without creating an endless “record the new HEAD in another commit” loop.

The repair task must document and normalize this protocol.

## Gate

M3 is **not closed yet**.

Authorized task: `TASK-M3-FIX-001`.

See `docs/M3_REPAIR_SPEC.md`.

M4 is not authorized.
