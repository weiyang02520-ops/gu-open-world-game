# Handoff — M4 Institutional Gate

## Reviewed baseline

M3 repair Gate:

`6d291afba23907768725ce9136414b673bdb3533`

## M4 result

M4 / TASK-M4-001 implementation is complete and ready for External ChatGPT review.

Delivered:

- three local factions with needs, states, memberships and offices;
- political blocs, influence and deterministic governance votes;
- institutional beliefs sourced from delivered M3 reports only;
- social identities, audience-scoped reputation and official standing;
- non-binary cases and deterministic investigation;
- recruitment, watch/sanction/close-case actions and faction missions;
- integrated M4 smoke and faction Save/Resume.

## Evidence to review

- `python -m pytest` passes 40 tests.
- M1, M2, M3 and M4 CLI smoke scenarios pass.
- M4 smoke demonstrates three factions, institutional belief, a disputed case, disagreement, official standing, recruitment and mission generation.
- CI installs the project and runs all four smoke commands.

## Stop

This task ends at `WAITING_FOR_MASTER` / `next_actor=chatgpt`. M5 is not started by this task.
