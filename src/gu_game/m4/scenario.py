"""Deterministic integrated M4 institutional smoke scenario."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..m2.scenario import scenario_attack_lands
from ..m3.engine import InformationEngine
from ..m3.models import BasisType, Channel, ReportClaim, ReportIntention
from .engine import FactionEngine
from .models import FactionProposalType


def run_m4_smoke(seed: int = 20260925) -> dict[str, Any]:
    combat, encounter_id = scenario_attack_lands(seed)
    simulation = combat.simulation
    information = InformationEngine.new(simulation)
    factions = FactionEngine.new(simulation, information)
    attacker, player = combat.encounters[encounter_id].participants
    witness = simulation.npc_ids[1]
    member = simulation.npc_ids[0]
    security_member = simulation.npc_ids[1]
    faction_id = "faction-grove-watch"
    player_identity = factions._identity_for_character(player)
    hit_event = next(event for event in simulation.world.event_log if event.event_type == "ATTACK_HIT")

    hypothesis = information.register_hypothesis("hyp:m4-player-dangerous", player, "dangerous", True)
    observation = information.observe_event(witness, hit_event.event_id, distance=4)
    assert observation is not None
    evidence = information.create_evidence(
        witness,
        observation.observation_id,
        evidence_type="WITNESS_TESTIMONY",
        supports=[(hypothesis.hypothesis_id, 10, 25)],
    )
    report = information.create_report(
        witness,
        member,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 30)],
        channel=Channel.FACE_TO_FACE,
        claimed_basis=BasisType.FIRST_HAND,
        actual_basis=BasisType.FIRST_HAND,
        evidence_references=[evidence.evidence_id],
        intention=ReportIntention.WARN,
    )
    information.advance_time(0)
    factions.ingest_report(faction_id, member, report.report_id)
    case = factions.open_case(faction_id, member, player_identity.identity_id, [hypothesis.hypothesis_id], [report.report_id])
    proposal = factions.create_proposal(
        faction_id,
        member,
        FactionProposalType.SANCTION_SUBJECT,
        target_identity_id=player_identity.identity_id,
        case_id=case.case_id,
        rationale=["SECURITY_NEED", "INSTITUTIONAL_BELIEF"],
        cost=70,
        risks=70,
    )
    factions.evaluate_proposal(proposal.proposal_id)
    mission = factions.generate_mission(faction_id, security_member, "INVESTIGATE")
    membership = factions.recruit(faction_id, player, member)
    factions.investigate_case(case.case_id, security_member, hit_event.event_id)

    return {
        "faction_summary": factions.summary(),
        "case_status": factions.cases[case.case_id].status.value,
        "proposal_status": factions.proposals[proposal.proposal_id].status,
        "votes": [vote.to_dict() for vote in factions.proposals[proposal.proposal_id].votes],
        "mission_id": mission.mission_id,
        "membership_status": membership.status.value,
        "standing": factions.standings[factions._standing_key(faction_id, player_identity.identity_id)].level.value,
        "event_count": len(simulation.world.event_log),
    }


def save_resume_m4(seed: int, path: str | Path) -> tuple[FactionEngine, str]:
    combat, encounter_id = scenario_attack_lands(seed)
    simulation = combat.simulation
    information = InformationEngine.new(simulation)
    factions = FactionEngine.new(simulation, information)
    faction_id = "faction-grove-watch"
    member = simulation.npc_ids[0]
    player = simulation.player_id
    identity = factions._identity_for_character(player)
    hypothesis = information.register_hypothesis("hyp:save-resume", player, "dangerous", True)
    report = information.create_report(
        member,
        member,
        [ReportClaim(hypothesis.hypothesis_id, True, True, 20)],
        channel=Channel.FACE_TO_FACE,
    )
    information.advance_time(0)
    factions.ingest_report(faction_id, member, report.report_id)
    factions.open_case(faction_id, member, identity.identity_id, [hypothesis.hypothesis_id], [report.report_id])
    factions.save(path)
    return factions, encounter_id
