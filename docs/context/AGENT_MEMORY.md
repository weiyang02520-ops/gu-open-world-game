# Agent Memory

## Current execution truth

- Repository: `weiyang02520-ops/gu-open-world-game`
- Branch: `main`
- Current milestone: M3 repair
- Active task: `TASK-M3-FIX-001`
- M0: PASS
- M1: PASS_WITH_NOTES
- M2: PASS_WITH_NOTES
- M3 review: CHANGES_REQUESTED
- Reviewed M3 Gate: `d13f7e71e5a7fa597c5d54efcc25d385eca54c09`

## Why repair is required

The M3 structure is good, but Master found:

- directional RelationshipState update is reversed on report delivery;
- SourceProfile expertise/honesty/bias/motive are mostly inert;
- rumor semantic mutation does not alter the receiver's interpreted belief;
- prior Gate SHA requirement was self-referential/impossible.

These are blocking because M4 institutional decisions will depend on M3 credibility and relationship semantics.

## Repair invariants

- receiver -> sender is the relevant relationship direction for trust in a received report;
- credibility must be deterministic and use declared source-profile dimensions;
- actual_basis remains hidden unless legitimately discovered;
- rumor mutation must affect interpreted claims while preserving origin-chain/correlation;
- investigations generate evidence, not direct truth;
- all old tests/smokes/save-resume remain deterministic;
- no M4 scope.

## Gate SHA semantics

Do not attempt to make a commit contain its own SHA.

Normalize workflow semantics so `last_codex_commit` means the last code-bearing Codex implementation commit. External Master resolves and verifies the actual current remote HEAD separately.

## User preference

Large useful work batches, manual control at major Gates. Do not stop for routine implementation questions.
