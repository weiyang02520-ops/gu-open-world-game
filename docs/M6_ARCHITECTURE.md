# M6 Cultivation, Breakthrough and Attainment

M6 is an incremental layer over the existing M1 Character/CultivationState and
M5 economy. It does not create a second Character or WorldClock authority.

## Rank-1 progression

Active minor stages:

INITIAL → MIDDLE → UPPER → PEAK

CultivationState remains the authoritative rank/stage/primeval-essence record.

M6 adds CultivationProfile for fatigue, instability, cultivation method,
breakthrough readiness and temporary health modifier.

Aptitude does not become generic XP. In V0.1 it influences aperture/capacity
growth at successful breakthrough.

## Cultivation sessions

A session consumes real primeval essence, world time, advances aperture-wall
progress and creates fatigue while sharing one authoritative clock.

M6 advances M5 economy/logistics first, then processes elapsed M3 information
and M4 institutional consequences against the already-advanced clock.
Therefore cultivation does not freeze caravans, Gu hunger, NPC activity or
pending information delivery.

## Breakthrough

- SAFE requires full wall progress and is condition-driven.
- SUPPORTED can start earlier with a real support material.
- FORCED can start at lower progress and uses deterministic seeded risk.

Failure may cause wall regression, instability, fatigue and temporary health
penalty. All thresholds are GAME_EXTENSION.

## Attainment

PathAttainmentState is separate from cultivation rank and from knowledge.
Active V0.1 realms are ORDINARY, QUASI_MASTER and MASTER.

InsightEvent increases attainment. Repeating the same source reduces novelty,
so grinding one identical observation is not equivalent to varied insight.

Knowledge is a separate KnowledgeRecord; learning a technique does not
automatically grant high attainment.

## Study / inheritance

V0.1 includes small GAME_EXTENSION sources such as the Weathered Ash
Inscription. They add knowledge and produce InsightEvent without becoming a
mandatory quest.

## Persistence

M6 serializes under WorldState.game_state["m6_cultivation"].
M1–M5 sibling layers remain in the same save.
