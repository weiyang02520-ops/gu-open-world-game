# M4 Institutional Architecture

M4 adds institutional actors over the M3 information boundary. Factions do not
read WorldTruth or the global event log directly. A member must receive a
report or deterministic investigation evidence before an institutional belief
can change.

## Layers

```text
NPC Belief / Relationship
        ↓ authorized report
FactionInstitutionalBelief
        ↓ needs + blocs + offices
FactionCase / FactionProposal
        ↓ deterministic votes
Official FactionStanding / Membership / Mission
```

The same identity can have a personal relationship, an audience-scoped
ReputationVector, a faction institutional belief and an official standing that
disagree. Membership is directional and is separate from loyalty and personal
relationship.

## Governance

The bootstrap creates three local GAME_EXTENSION factions, each with council
and security offices and two interest blocs. Proposal scores use faction need,
bloc priorities, risk tolerance, cost and office influence. Vote results and
reasons are durable events. Approved proposals apply official standing or
create missions; rejected proposals do not mutate policy.

## Cases and investigations

Reports open rumor or investigation cases rather than instant guilt. Faction
investigation calls M3's deterministic event-trace rule to create an
Observation/Evidence item. It can move a case to `DISPUTED` or `CONFIRMED`
without a truth-reveal shortcut.

## Save state and smoke

M4 state is stored under `WorldState.game_state["m4_factions"]`; M1, M2 and M3
layers remain alongside it. The headless smoke is:

```powershell
python -m gu_game --scenario m4 --seed 20260925
```

It demonstrates three factions, offices, blocs, institutional belief, a
disputed case, disagreeing votes, official standing, recruitment and a need-
driven mission.
