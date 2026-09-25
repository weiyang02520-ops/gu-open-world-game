from pathlib import Path

from gu_game.m1.simulation import Simulation
from gu_game.m2.scenario import scenario_attack_lands
from gu_game.m3.engine import InformationEngine
from gu_game.m4.engine import FactionEngine
from gu_game.m4.models import FactionCaseStatus, FactionProposalType, FactionStandingLevel
from gu_game.m4.scenario import run_m4_smoke, save_resume_m4


def test_bootstrap_has_three_factions_memberships_offices_and_blocs() -> None:
    simulation = Simulation.new(20260925)
    factions = FactionEngine.new(simulation, InformationEngine.new(simulation))

    assert len(factions.definitions) >= 3
    assert len(factions.memberships) >= len(simulation.characters) * 3
    assert len(factions.offices) >= 6
    assert len(factions.blocs) >= 6
    assert all(faction_id in factions.states for faction_id in factions.definitions)


def test_m4_smoke_has_disagreement_case_mission_recruitment_and_separate_standing() -> None:
    result = run_m4_smoke(20260925)

    assert result["faction_summary"]["factions"] == 3
    assert result["case_status"] == FactionCaseStatus.DISPUTED.value
    assert result["proposal_status"] == "REJECTED"
    assert {vote["approve"] for vote in result["votes"]} == {True, False}
    assert result["mission_id"]
    assert result["membership_status"] == "AFFILIATE"
    assert result["standing"] == FactionStandingLevel.GUEST.value


def test_absent_institution_does_not_confirm_hidden_event() -> None:
    simulation = Simulation.new(20260925)
    information = InformationEngine.new(simulation)
    factions = FactionEngine.new(simulation, information)
    faction_id = "faction-grove-watch"
    opener = simulation.npc_ids[0]
    identity = factions._identity_for_character(simulation.player_id)
    case = factions.open_case(faction_id, opener, identity.identity_id, ["hyp:hidden"], [])

    assert case.status is not FactionCaseStatus.CONFIRMED


def test_m4_save_resume_preserves_institutional_state(tmp_path: Path) -> None:
    path = tmp_path / "m4-state.json"
    factions, _ = save_resume_m4(20260925, path)
    restored = FactionEngine.load(path)

    assert restored.to_dict() == factions.to_dict()
    assert restored.summary() == factions.summary()


def test_reputation_is_audience_scoped_and_separate_from_official_standing() -> None:
    simulation = Simulation.new(20260925)
    factions = FactionEngine.new(simulation, InformationEngine.new(simulation))
    identity = factions._identity_for_character(simulation.player_id)
    reputation = factions.set_reputation("faction-grove-watch", identity.identity_id, danger=80, trust=20)
    standing = factions.standings[factions._standing_key("faction-grove-watch", identity.identity_id)]

    assert reputation.audience_id == "faction:faction-grove-watch"
    assert reputation.danger == 80 and reputation.trust == 20
    assert standing.level is FactionStandingLevel.UNKNOWN


def test_m4_smoke_is_deterministic() -> None:
    assert run_m4_smoke(20260925) == run_m4_smoke(20260925)
