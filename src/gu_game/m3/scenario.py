"""Deterministic integrated M3 information smoke scenario."""

from __future__ import annotations

from typing import Any

from ..m2.scenario import scenario_attack_lands
from .engine import InformationEngine
from .models import BasisType, Channel, ReportClaim, ReportIntention


def run_m3_smoke(seed: int = 20260925) -> dict[str, Any]:
    combat, encounter_id = scenario_attack_lands(seed)
    simulation = combat.simulation
    info = InformationEngine.new(simulation)
    attacker, player = combat.encounters[encounter_id].participants
    witness = simulation.npc_ids[1]
    absent = simulation.npc_ids[2]

    initiated_by_attacker = info.register_hypothesis(
        "hyp:attacker-initiated",
        subject_id=attacker,
        predicate="initiated_attack",
        object_value=True,
    )
    player_initiated = info.register_hypothesis(
        "hyp:player-initiated",
        subject_id=player,
        predicate="initiated_attack",
        object_value=True,
    )
    player_dangerous = info.register_hypothesis(
        "hyp:player-dangerous",
        subject_id=player,
        predicate="dangerous",
        object_value=True,
    )

    hit_event = next(event for event in simulation.world.event_log if event.event_type == "ATTACK_HIT")
    observation = info.observe_event(witness, hit_event.event_id, distance=4)
    assert observation is not None
    info.create_evidence(
        witness,
        observation.observation_id,
        evidence_type="WITNESS_TESTIMONY",
        supports=[
            (initiated_by_attacker.hypothesis_id, 35, 0),
            (player_initiated.hypothesis_id, 0, 35),
            (player_dangerous.hypothesis_id, 8, 10),
        ],
    )
    witness_report = info.create_report(
        witness,
        witness,
        [
            ReportClaim(initiated_by_attacker.hypothesis_id, True, True, 90),
            ReportClaim(player_initiated.hypothesis_id, True, False, 80),
            ReportClaim(player_dangerous.hypothesis_id, True, False, 70),
        ],
        claimed_basis=BasisType.FIRST_HAND,
        actual_basis=BasisType.FIRST_HAND,
        intention=ReportIntention.INFORM,
    )
    # Face-to-face self-delivery makes the witness's direct conclusion explicit.
    info.advance_time(0)

    false_report = info.create_report(
        attacker,
        absent,
        [
            ReportClaim(player_initiated.hypothesis_id, True, True, 85),
            ReportClaim(player_dangerous.hypothesis_id, True, True, 85),
        ],
        channel=Channel.MESSENGER,
        claimed_basis=BasisType.FIRST_HAND,
        actual_basis=BasisType.DELIBERATE_LIE,
        intention=ReportIntention.FRAME,
    )
    rumor = info.create_rumor(
        false_report.report_id,
        absent,
        channel=Channel.LOCAL_NETWORK,
        semantic_slots={"initiator": player, "action": "ATTACK", "location": "southern-grove"},
    )
    before_delivery = info.decide(absent, player, player_dangerous.hypothesis_id)
    info.advance_time(7_200)
    after_delivery = info.decide(absent, player, player_dangerous.hypothesis_id)

    investigation = info.investigate_scene(
        absent,
        hit_event.event_id,
        supports=[
            (initiated_by_attacker.hypothesis_id, 40, 0),
            (player_initiated.hypothesis_id, 0, 40),
            (player_dangerous.hypothesis_id, 0, 70),
        ],
    )
    corrected = info.decide(absent, player, player_dangerous.hypothesis_id)
    return {
        "event_id": hit_event.event_id,
        "witness_report_id": witness_report.report_id,
        "false_report_id": false_report.report_id,
        "rumor_id": rumor.rumor_id,
        "investigation_evidence_id": investigation.evidence_id if investigation else None,
        "before_delivery": before_delivery.to_dict(),
        "after_delivery": after_delivery.to_dict(),
        "corrected": corrected.to_dict(),
        "beliefs": {
            "witness": {
                key: value.to_dict() for key, value in info.beliefs.get(witness, {}).items()
            },
            "absent": {
                key: value.to_dict() for key, value in info.beliefs.get(absent, {}).items()
            },
        },
        "rumor_slots": info.rumors[rumor.rumor_id].semantic_slots,
        "event_count": len(simulation.world.event_log),
    }
