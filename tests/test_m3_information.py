from pathlib import Path

from gu_game.m1.simulation import Simulation
from gu_game.m2.engine import CombatEngine
from gu_game.m2.models import CombatGuRole
from gu_game.m2.scenario import scenario_attack_lands
from gu_game.m3.engine import InformationEngine
from gu_game.m3.models import BasisType, Channel, ReportClaim, ReportIntention
from gu_game.m3.scenario import run_m3_smoke


def _information_from_combat(seed: int = 20260925) -> tuple[InformationEngine, str, str, str]:
    combat, encounter_id = scenario_attack_lands(seed)
    attacker, player = combat.encounters[encounter_id].participants
    event = next(item for item in combat.world.event_log if item.event_type == "ATTACK_HIT")
    return InformationEngine.new(combat.simulation), event.event_id, attacker, player


def test_m3_smoke_produces_different_decisions_and_mutates_rumor_slots() -> None:
    result = run_m3_smoke(20260925)

    assert result["before_delivery"]["action"] == "ASK"
    assert result["after_delivery"]["action"] == "AVOID_TARGET"
    assert result["corrected"]["action"] == "ASK"
    assert result["rumor_slots"]["initiator"] == "unknown-third-party"
    assert result["event_count"] > 0


def test_observation_is_incomplete_and_does_not_copy_hidden_combat_state() -> None:
    info, event_id, attacker, player = _information_from_combat()
    witness = info.simulation.npc_ids[1]
    observation = info.observe_event(witness, event_id, distance=4)

    assert observation is not None
    assert "primeval_current" not in observation.perceived_features
    assert "injury_dictionary" not in observation.perceived_features
    assert "target_essence" not in observation.perceived_features


def test_false_report_changes_belief_without_mutating_world_truth() -> None:
    info, event_id, attacker, player = _information_from_combat()
    receiver = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis("hyp:false", player, "initiated_attack", True)
    original_event = info._event(event_id).to_dict()
    report = info.create_report(
        attacker,
        receiver,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 90)],
        channel=Channel.FACE_TO_FACE,
        claimed_basis=BasisType.FIRST_HAND,
        actual_basis=BasisType.DELIBERATE_LIE,
        intention=ReportIntention.FRAME,
    )
    info.advance_time(0)

    assert info.belief(receiver, hypothesis.hypothesis_id) is not None
    assert info._event(event_id).to_dict() == original_event
    assert info.reports[report.report_id].actual_basis is BasisType.DELIBERATE_LIE


def test_correlated_reports_are_discounted_against_independent_evidence() -> None:
    info, _, sender, _ = _information_from_combat()
    receiver = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis("hyp:correlation", sender, "dangerous", True)
    group = "same-origin"

    info.create_report(
        sender,
        receiver,
            [ReportClaim(hypothesis.hypothesis_id, True, True, 10)],
        origin_chain_id="chain-1",
        independence_group_id=group,
    )
    info.advance_time(0)
    first = info.belief(receiver, hypothesis.hypothesis_id).confidence
    info.create_report(
        sender,
        receiver,
            [ReportClaim(hypothesis.hypothesis_id, True, True, 10)],
        origin_chain_id="chain-1",
        independence_group_id=group,
    )
    info.advance_time(0)
    repeated_gain = info.belief(receiver, hypothesis.hypothesis_id).confidence - first
    info.create_report(
        info.simulation.player_id,
        receiver,
            [ReportClaim(hypothesis.hypothesis_id, True, True, 10)],
        origin_chain_id="independent-chain",
        independence_group_id="independent-group",
    )
    info.advance_time(0)
    independent_gain = info.belief(receiver, hypothesis.hypothesis_id).confidence - first - repeated_gain

    assert repeated_gain > 0
    assert independent_gain > repeated_gain


def test_delayed_report_and_pending_transmission_survive_save_resume(tmp_path: Path) -> None:
    info, _, sender, player = _information_from_combat()
    receiver = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis("hyp:delayed", player, "dangerous", True)
    info.create_report(
        sender,
        receiver,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 80)],
        channel=Channel.MESSENGER,
    )
    assert info.belief(receiver, hypothesis.hypothesis_id) is None
    path = tmp_path / "m3-pending.json"
    info.save(path)

    info.advance_time(7_200)
    uninterrupted = info.to_dict()
    uninterrupted_events = [event.to_dict() for event in info.world.event_log]

    resumed = InformationEngine.load(path)
    resumed.advance_time(7_200)
    assert resumed.to_dict() == uninterrupted
    assert [event.to_dict() for event in resumed.world.event_log] == uninterrupted_events
    assert resumed.belief(receiver, hypothesis.hypothesis_id) is not None


def test_same_execute_time_combat_actions_keep_sequence_order() -> None:
    simulation = Simulation.new(20260925)
    combat = CombatEngine.new(simulation)
    first_attacker, second_attacker = simulation.npc_ids[0], simulation.npc_ids[1]
    player = simulation.player_id
    encounter = combat.start_encounter(
        (first_attacker, second_attacker, player),
        positions={first_attacker: 0, second_attacker: 2, player: 4},
    )
    combat.declare_attack(
        encounter.encounter_id,
        first_attacker,
        player,
        combat.profile_for_role(first_attacker, CombatGuRole.ATTACK).profile_id,
    )
    combat.declare_attack(
        encounter.encounter_id,
        second_attacker,
        player,
        combat.profile_for_role(second_attacker, CombatGuRole.ATTACK).profile_id,
    )
    combat.advance_ticks(encounter.encounter_id, 4)
    hits = [
        event.actor_id
        for event in combat.world.event_log
        if event.event_type == "ATTACK_HIT"
    ]
    assert hits[:2] == [first_attacker, second_attacker]


def test_relationship_report_update_is_receiver_to_sender_only() -> None:
    info, _, sender, _ = _information_from_combat()
    receiver = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis("hyp:relationship", sender, "dangerous", True)
    info.create_report(
        sender,
        receiver,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 90)],
        channel=Channel.FACE_TO_FACE,
    )
    info.advance_time(0)

    assert info.relationship(receiver, sender).trust > 50
    assert info.relationship(sender, receiver).trust == 50


def _report_impact(
    *, trustworthiness: int = 50, expertise: int = 50, honesty: int = 50, motive: int = 0, relationship_trust: int = 50
) -> int:
    info, _, sender, _ = _information_from_combat()
    receiver = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis(f"hyp:impact-{trustworthiness}-{expertise}-{honesty}-{motive}", sender, "dangerous", True)
    info.set_source_profile(
        receiver,
        sender,
        trustworthiness=trustworthiness,
        domain_expertise=expertise,
        honesty_history=honesty,
        motive_modifier=motive,
    )
    info.relationship(receiver, sender).trust = relationship_trust
    info.create_report(
        sender,
        receiver,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 10)],
        channel=Channel.FACE_TO_FACE,
    )
    info.advance_time(0)
    return info.belief(receiver, hypothesis.hypothesis_id).confidence


def test_all_source_profile_dimensions_change_report_impact() -> None:
    base = _report_impact()
    assert _report_impact(trustworthiness=90) > base
    assert _report_impact(expertise=90) > base
    assert _report_impact(honesty=90) > base
    assert _report_impact(motive=-30) < base
    assert _report_impact(relationship_trust=90) > base


def test_contradictory_evidence_updates_only_evaluators_source_profile() -> None:
    info, event_id, sender, _ = _information_from_combat()
    evaluator = info.simulation.npc_ids[2]
    other = info.simulation.npc_ids[1]
    hypothesis = info.register_hypothesis("hyp:credibility-feedback", sender, "dangerous", True)
    info.create_report(
        sender,
        evaluator,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 20)],
        channel=Channel.FACE_TO_FACE,
    )
    info.advance_time(0)
    observation = info.observe_event(evaluator, event_id, distance=4)
    assert observation is not None
    info.create_evidence(
        evaluator,
        observation.observation_id,
        evidence_type="WOUND_PATTERN",
        supports=[(hypothesis.hypothesis_id, 0, 80)],
    )

    evaluator_profile = info.source_profiles[info._source_key(evaluator, sender)]
    assert evaluator_profile.trustworthiness < 50
    assert evaluator_profile.honesty_history < 50
    assert info._source_key(other, sender) not in info.source_profiles


def test_rumor_mutation_changes_receiver_belief_interpretation() -> None:
    info, _, sender, player = _information_from_combat()
    receiver = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis("hyp:mutated-initiator", player, "initiated_attack", True)
    report = info.create_report(
        sender,
        receiver,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 30)],
        channel=Channel.LOCAL_NETWORK,
    )
    rumor = info.create_rumor(
        report.report_id,
        receiver,
        channel=Channel.LOCAL_NETWORK,
        semantic_slots={"initiator": player},
    )
    info.advance_time(1_800)

    derived = [item for item in info.reports.values() if item.parent_report_id == report.report_id]
    assert derived
    assert any(
        claim.hypothesis_id.startswith(f"derived:{rumor.rumor_id}:")
        for item in derived
        for claim in item.claims
    )
    assert any(
        hypothesis_id.startswith(f"derived:{rumor.rumor_id}:")
        for hypothesis_id in info.beliefs.get(receiver, {})
    )


def test_multi_hop_rumor_preserves_lineage_and_correlation() -> None:
    info, _, sender, player = _information_from_combat()
    hop_one = info.simulation.npc_ids[1]
    hop_two = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis("hyp:multi-hop", player, "initiated_attack", True)
    original = info.create_report(
        sender,
        hop_one,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 25)],
        channel=Channel.FACE_TO_FACE,
    )
    info.advance_time(0)
    rumor_one = info.create_rumor(
        original.report_id,
        hop_one,
        channel=Channel.LOCAL_NETWORK,
        semantic_slots={"initiator": player},
    )
    info.advance_time(1_800)
    first_derived = next(item for item in info.reports.values() if item.parent_report_id == original.report_id)
    rumor_two = info.create_rumor(first_derived.report_id, hop_two, channel=Channel.LOCAL_NETWORK)
    info.advance_time(1_800)
    second_derived = next(item for item in info.reports.values() if item.parent_report_id == first_derived.report_id)

    assert second_derived.origin_chain_id == original.origin_chain_id
    assert second_derived.independence_group_id == original.independence_group_id
    assert rumor_two.origin_chain_id == rumor_one.origin_chain_id
    assert rumor_two.mutation_level >= rumor_one.mutation_level
    assert any(key.startswith("derived:") for key in info.beliefs.get(hop_two, {}))


def test_direct_evidence_upgrades_rumor_category_and_slower_decay() -> None:
    info, event_id, sender, player = _information_from_combat()
    receiver = info.simulation.npc_ids[2]
    hypothesis = info.register_hypothesis("hyp:mixed-category", player, "dangerous", True)
    report = info.create_report(
        sender,
        receiver,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 10)],
        channel=Channel.FACE_TO_FACE,
    )
    info.advance_time(0)
    assert info.belief(receiver, hypothesis.hypothesis_id).category == "RUMOR"
    observation = info.observe_event(receiver, event_id, distance=4)
    assert observation is not None
    info.create_evidence(
        receiver,
        observation.observation_id,
        evidence_type="WOUND_PATTERN",
        supports=[(hypothesis.hypothesis_id, 80, 0)],
    )
    belief = info.belief(receiver, hypothesis.hypothesis_id)
    assert belief.category == "IMMEDIATE"
    before = belief.confidence
    info.advance_time(3_600)
    assert info.belief(receiver, hypothesis.hypothesis_id).confidence >= before - 8
