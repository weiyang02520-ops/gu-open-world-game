# V0.1 Durable Event Catalog

> Scope: the durable event families exercised by the current headless V0.1.
> Source of truth remains code + `WorldState.event_log`.

## Event authority

All durable domain events ultimately enter:

`WorldState.event_log`

through the shared EventBus.

The event log is ordered, saveable and deterministic for the same seed/actions.

## M1 — Character / Gu / resources / market / time

- `RESOURCE_GATHERED`
- `RESOURCE_REGENERATED`
- `MARKET_BUY`
- `MARKET_SELL`
- `GU_FED`
- `GU_HUNGER_CHANGED`
- `GU_CONDITION_CHANGED`
- `CULTIVATION_PROGRESS`
- `NPC_ACTION_SELECTED`
- `TIME_ADVANCED`

## M2 — Combat / reaction / injury

- `COMBAT_STARTED`
- `COMBAT_ACTION_DECLARED`
- `GU_ACTIVATION_STARTED`
- `THREAT_PERCEIVED`
- `THREAT_NOT_PERCEIVED`
- `REACTION_SELECTED`
- `GU_ACTIVATED`
- `ATTACK_EVADED`
- `ATTACK_MISSED`
- `ATTACK_HIT`
- `INJURY_APPLIED`
- `BLOOD_LOSS_CHANGED`
- `FLEE_ATTEMPTED`
- `COMBAT_ENDED`

## M3 — Information / belief / memory

- `OBSERVATION_CREATED`
- `EVIDENCE_DISCOVERED`
- `REPORT_CREATED`
- `REPORT_DELIVERED`
- `RUMOR_CREATED`
- `RUMOR_SPREAD`
- `RUMOR_MUTATED`
- `BELIEF_UPDATED`
- `MEMORY_FORMED`
- `RELATIONSHIP_CHANGED`
- `SOURCE_CREDIBILITY_UPDATED`
- `INVESTIGATION_STARTED`
- `INVESTIGATION_RESULT`
- `INFORMATION_ACTION_SELECTED`

## M4 — Institutional / faction

- `INSTITUTIONAL_BELIEF_UPDATED`
- `FACTION_CASE_OPENED`
- `FACTION_INVESTIGATION_RESULT`
- `FACTION_PROPOSAL_CREATED`
- `FACTION_VOTE_CAST`
- `FACTION_PROPOSAL_RESOLVED`
- `FACTION_STANDING_CHANGED`
- `MEMBERSHIP_CHANGED`
- `FACTION_MISSION_CREATED`
- `FACTION_MISSION_ACCEPTED`
- `FACTION_MISSION_PROGRESS`
- `FACTION_MISSION_COMPLETED`
- `FACTION_MISSION_EXPIRED`

## M5 — Economy / shortage / logistics

- `M5_RESOURCE_GATHERED`
- `M5_RESOURCE_REGENERATED`
- `M5_MARKET_PRICE_CHANGED`
- `M5_MARKET_RUMOR_RECEIVED`
- `M5_SHORTAGE_DECLARED`
- `M5_SHORTAGE_RESOLVED`
- `M5_ROUTE_RISK_CHANGED`
- `M5_SHIPMENT_DEPARTED`
- `M5_SHIPMENT_ARRIVED`
- `M5_SHIPMENT_LOST`
- `M5_FACTION_PROCUREMENT_ORDERED`

Market trades continue to use `MARKET_BUY` / `MARKET_SELL`.

## M6 — Cultivation / breakthrough / attainment

- `M6_CULTIVATION_SESSION`
- `M6_ABSTRACT_CULTIVATION_SESSION`
- `M6_CULTIVATION_RESTED`
- `M6_BREAKTHROUGH_RESOLVED`
- `M6_INSIGHT_GAINED`
- `M6_STUDY_COMPLETED`

The abstract cultivation event is used by remote LOD actors when world time has already advanced.

## M7 — Effect Graph / killer moves

- `M7_EFFECT_NODE_EXECUTED`
- `M7_KILLER_MOVE_DISCOVERED`
- `M7_KILLER_MOVE_RESEARCHED`
- `M7_KILLER_MOVE_EXECUTED`
- `M7_KILLER_MOVE_BACKLASH`

M7 may also create ordinary combat events such as `INJURY_APPLIED` through its M2 integration.

## M8 — Integrated world consequences

- `M8_TRAVEL_COMPLETED`
- `M8_REMOTE_NPC_ACTION`
- `M8_RESOURCE_PRESSURE_VISIBLE`
- `M8_MARKET_THEFT`
- `M8_NPC_GOAL_CHANGED`
- `M8_SUPPLY_MISSION_DELIVERED`
- `M8_SHIPMENT_ROBBED`
- `M8_FACTION_RESERVE_RELEASED`
- `M8_CANON_ANCHOR_RESOLVED`

M8 intentionally reuses lower-layer events rather than inventing duplicate integrated equivalents.

## Causality rule

The event log is an audit trail, not a separate authority.

State changes must be explainable by:

```text
validated action / scheduled system update
→ domain event(s)
→ authoritative state mutation
→ later system consequences
```

The final same-seed cooperative/adversarial comparison is accepted only when its divergent state is backed by divergent durable event chains.
