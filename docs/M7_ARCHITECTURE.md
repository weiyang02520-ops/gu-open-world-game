# M7 Effect Graph and Killer-Move Prototype

M7 keeps M2 combat as the timing/injury authority and M6 attainment as the
control/understanding authority.

## Effect Graph

Each graph is a deterministic sequence of typed nodes. V0.1 node types include:

- DELAY
- DETECT
- MOVE
- CHECK_RANGE
- APPLY_INJURY
- APPLY_STATUS (reserved)
- END

Existing M2 attack/movement/perception CombatGuProfiles are mirrored into
serializable EffectGraphs so legacy combat behavior remains available while
new combinations can be described compositionally.

## Killer moves

A KillerMoveDefinition stores:

- core and auxiliary Gu;
- path;
- activation order;
- EffectGraph;
- essence cost;
- preparation time;
- complexity;
- stability;
- minimum attainment;
- GAME_EXTENSION provenance.

KillerMoveInstance stores owner-specific mastery and research improvement.

## Attainment interaction

Attainment changes complexity ceiling and stability. It does not add a flat
damage multiplier.

ORDINARY controls only small combinations, QUASI_MASTER controls larger ones,
and MASTER has the highest V0.1 complexity ceiling.

## Stability and backlash

Low-stability moves can fail before graph execution, consuming essence,
damaging the user and straining component Gu. Highly researched PROFICIENT+
moves execute without random CI flakiness.

## Research

Research consumes real refinement material from M5, consumes world time via
M6, generates an EXPERIMENTATION InsightEvent, and improves stability/mastery.

## Combat integration

EffectGraph DELAY nodes advance the M2 integer combat clock. MOVE changes the
actual CombatEncounter position. APPLY_INJURY uses the M2 BodyState injury
model. No second combat authority is created.

## Persistence

M7 serializes under WorldState.game_state["m7_killer_moves"].
