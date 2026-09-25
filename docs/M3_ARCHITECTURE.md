# M3 Information Architecture

M3 separates authoritative `WorldState` from what each NPC has observed,
heard, remembered and believed. No report or rumor can mutate the underlying
event truth.

## Truth boundary

```text
World Event
  -> rule-gated Observation
  -> Evidence + EvidenceSupport
  -> InformationReport
  -> delayed Transmission / RumorThread
  -> per-character BeliefRecord
  -> MemoryRecord / RelationshipState
  -> InformationDecision
```

`Observation.perceived_features` is a deliberately small projection. Combat
events may expose a visible actor, target count, coarse body part or movement
signal, but never copy primeval essence or the complete injury dictionary into
belief state. Active M2 combat may still use its immediate perceptual snapshot;
off-screen and social decisions use M3 records.

## Structured hypotheses and evidence

`Hypothesis` stores subject, predicate, object value and parameters. Belief
stores map each NPC to structured hypotheses rather than free-text opinions.
`EvidenceItem` carries origin event/observation, quality, authenticity,
tampering, an independence group and explicit support/contradiction strengths.

## Reports and correlated sources

`InformationReport` persists claimed basis separately from actual internal
basis. A sender can claim `FIRST_HAND` while the engine records
`DELIBERATE_LIE`; the receiver only updates from the claimed basis and source
profile. `origin_chain_id` and `independence_group_id` survive every retelling.
Repeated reports in one origin group are divided by a deterministic
GAME_EXTENSION correlation factor, while independent evidence receives a
separate corroboration bonus.

## Belief, memory and relationships

Beliefs use bounded integer confidence and certainty classes. Rumors decay
faster than immediate observations; significant violence creates persistent
memories even when confidence later decays. Relationships have independent
trust, fear, respect, resentment and favor dimensions.

## Channels and investigation

Face-to-face, market gossip, messenger and local network channels have
deterministic delays and transmission quality. Pending transmissions are part
of the save state and are delivered in `(deliver_at, sequence)` order.

`investigate_scene` first creates a new observation and evidence item. It does
not call a truth-reveal shortcut; any belief correction comes from the new
evidence support/contradiction relations.

## Save state and CLI

M3 state is stored under `WorldState.game_state["m3_information"]`, alongside
the optional M2 layer. Existing M1/M2 saves without this key remain loadable.

```powershell
python -m gu_game --scenario m3 --seed 20260925
```

The smoke scenario combines an M2 attack event, a direct witness, a delayed
false report, a mutated rumor, two different decisions and an investigation.
