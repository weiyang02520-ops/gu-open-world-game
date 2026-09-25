# Master Review

## M2 / TASK-M2-001

- Reviewed remote HEAD: `60b4b776ef18c5992ceb6b7ed3131feac7f17469`
- Verdict: **PASS_WITH_NOTES**
- Reviewer: External ChatGPT Web Master
- Date: 2026-09-25

## Verified from remote implementation

- integer millisecond combat time with deterministic `(execute_at_ms, sequence)` ordering;
- serializable `CombatEncounter`;
- six body parts, bleeding, impairment, incapacitation/death;
- attack / movement / perception Gu roles over real owned Gu instances;
- preparation → perception → reaction → resolution pipeline;
- real primeval essence costs and integer local positions;
- reaction can change attack outcome;
- leg injury changes later movement;
- NPC ATTACK/HOLD/FLEE through `PerceivedCombatSnapshot`;
- active-combat save/resume determinism;
- M1 save compatibility and M1 regressions;
- final Gate HEAD CI success.

## Result

M2 fulfills its product question. Combat is no longer a direct HP subtraction loop: time, perception, reaction, movement, essence and concrete injury all affect outcomes.

M2 is closed.

## Notes carried into M3

1. `PerceivedCombatSnapshot.target_movement_impairment` is currently derived from authoritative body state. This is acceptable as an immediate visible combat signal, but M3 must formalize the truth→observation boundary and prevent exact hidden injury data from leaking into persistent beliefs.
2. Equal-time ordering is correctly implemented by `(execute_at_ms, sequence)`, but there is no dedicated regression test asserting two same-time actions resolve by sequence. M3 must add this test.
3. Codex Gate bookkeeping still recorded `last_codex_commit` as the implementation commit rather than the final Gate HEAD. Future Gate state must record the exact final pushed Codex HEAD.

## Gate

M3 / TASK-M3-001 is authorized.

Do not begin M4 without a new Master review.
