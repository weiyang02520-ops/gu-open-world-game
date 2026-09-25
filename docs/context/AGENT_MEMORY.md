# Agent Memory

## Current execution truth

- Repository: `weiyang02520-ops/gu-open-world-game`
- Branch: `main`
- Current milestone: M3
- Current task: `TASK-M3-001`
- M0: PASS
- M1: PASS_WITH_NOTES
- M2: PASS_WITH_NOTES
- M2 reviewed HEAD: `60b4b776ef18c5992ceb6b7ed3131feac7f17469`
- M3 is authorized.

Read `docs/M3_TASK_SPEC.md` plus product/roadmap/execution-policy docs before coding.

## User working preference

The user prefers large useful work packages and manual control at major Gates.

Within M3, continue through implementation, tests, smoke, docs and verification without asking routine micro-questions.

## Stable constraints

- deterministic WorldClock/RNG;
- one durable event log;
- versioned save state;
- no wall-clock or unseeded random;
- unsourced coefficients are GAME_EXTENSION;
- Player/NPC share world rules;
- Canon/Fan/Game provenance remains first-class;
- NPCs must not gain omniscient WorldTruth;
- no generic Character EXP.

## Delivered baseline

M1:
- living Day 1–2 economy/cultivation/Gu loop.

M2:
- integer-ms combat;
- CombatEncounter;
- body-part injury;
- attack/movement/perception Gu roles;
- Reaction Window;
- flee/disengage;
- PerceivedCombatSnapshot;
- combat save/resume.

## M3 hard requirements

- structured hypotheses;
- incomplete Observation;
- Evidence and EvidenceSupport;
- Report with claimed/actual basis and intention;
- source credibility;
- origin-chain / independence-group lineage;
- correlated-source discount;
- per-NPC beliefs that may be wrong;
- belief decay;
- memories;
- multidimensional relationships;
- delayed rumor channels;
- structured rumor mutation;
- minimal investigation;
- information-aware NPC actions;
- save/resume exactness;
- absent NPC cannot know events before delivery.

## Carried review notes

- M2 visible movement impairment must become a formal perceptual signal rather than persistent direct truth leakage.
- Add explicit same-execute-time combat sequence ordering test.
- At Gate, `last_codex_commit` must equal exact final pushed Codex HEAD.

## Stop

At M3 completion: test/smoke/docs/report → commit/push/exact remote verify → WAITING_FOR_MASTER / chatgpt → STOP before M4.
