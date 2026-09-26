"""Deterministic local faction and institutional governance layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..m1.simulation import Simulation
from ..m3.engine import InformationEngine
from ..m3.models import Hypothesis
from ..save import load_world, save_world
from .balance import GAME_EXTENSION_FACTION_BALANCE as B
from .models import (
    FactionCase,
    FactionCaseStatus,
    FactionDefinition,
    FactionMission,
    FactionNeed,
    FactionProposal,
    FactionProposalType,
    FactionStanding,
    FactionStandingLevel,
    FactionState,
    InfluenceVector,
    InstitutionalBelief,
    Membership,
    MembershipStatus,
    OfficeAssignment,
    PoliticalBloc,
    ReputationVector,
    SocialIdentity,
    Vote,
)


class FactionValidationError(ValueError):
    pass


class FactionEngine:
    M4_SCHEMA_VERSION = 1

    def __init__(self, simulation: Simulation, information: InformationEngine) -> None:
        self.simulation = simulation
        self.information = information
        self.world = simulation.world
        self.event_bus = simulation.event_bus
        self.definitions: dict[str, FactionDefinition] = {}
        self.states: dict[str, FactionState] = {}
        self.needs: dict[str, FactionNeed] = {}
        self.memberships: dict[str, Membership] = {}
        self.offices: dict[str, OfficeAssignment] = {}
        self.blocs: dict[str, PoliticalBloc] = {}
        self.institutional_beliefs: dict[str, InstitutionalBelief] = {}
        self.identities: dict[str, SocialIdentity] = {}
        self.reputations: dict[str, ReputationVector] = {}
        self.standings: dict[str, FactionStanding] = {}
        self.cases: dict[str, FactionCase] = {}
        self.proposals: dict[str, FactionProposal] = {}
        self.influence: dict[str, InfluenceVector] = {}
        self.missions: dict[str, FactionMission] = {}
        self._sequence = 0

    @classmethod
    def new(cls, simulation: Simulation, information: InformationEngine) -> "FactionEngine":
        engine = cls(simulation, information)
        engine._bootstrap()
        return engine

    @classmethod
    def from_simulation(cls, simulation: Simulation, information: InformationEngine) -> "FactionEngine":
        engine = cls(simulation, information)
        data = simulation.world.game_state.get("m4_factions")
        if data:
            engine._load_dict(data)
        else:
            engine._bootstrap()
        return engine

    @classmethod
    def load(cls, path: str | Path) -> "FactionEngine":
        world = load_world(path)
        simulation = Simulation.from_world_state(world)
        information = InformationEngine.from_simulation(simulation)
        return cls.from_simulation(simulation, information)

    def save(self, path: str | Path) -> Path:
        self._sync_world_state()
        return save_world(self.world, path)

    def _bootstrap(self) -> None:
        faction_specs = (
            ("faction-grove-watch", "Grove Watch", "SECURITY", "council"),
            ("faction-river-traders", "River Traders", "TRADE", "council"),
            ("faction-ash-study", "Ash Study Hall", "CULTIVATION", "leader"),
        )
        for faction_id, name, faction_type, governance in faction_specs:
            self.definitions[faction_id] = FactionDefinition(
                faction_id, name, faction_type, "location-southern-grove", governance
            )
            self.states[faction_id] = FactionState(
                faction_id, 180, ["location-southern-grove"], 50, 70, 60, 40
            )
            self.needs[f"{faction_id}:security"] = FactionNeed(
                f"{faction_id}:security", faction_id, "SECURITY", B["security_need_default"]
            )
            self.needs[f"{faction_id}:recruitment"] = FactionNeed(
                f"{faction_id}:recruitment", faction_id, "RECRUITMENT", B["recruitment_need_default"]
            )
            for bloc_name, priority in (("SECURITY_HARDLINERS", {"SECURITY": 90, "RISK": 80}), ("TRADE_PRAGMATISTS", {"REVENUE": 85, "RISK": 25})):
                bloc_id = self._id("bloc")
                self.blocs[bloc_id] = PoliticalBloc(bloc_id, faction_id, bloc_name, [], priority, 50, priority["RISK"])

        for character_id, character in self.simulation.characters.items():
            identity_id = self._id("identity")
            self.identities[identity_id] = SocialIdentity(identity_id, character_id, character.name, [])
            self.identities[identity_id].known_by.append("public")
            for faction_id in self.definitions:
                key = self._membership_key(character_id, faction_id)
                self.memberships[key] = Membership(character_id, faction_id)
                self.standings[self._standing_key(faction_id, identity_id)] = FactionStanding(
                    faction_id, identity_id, FactionStandingLevel.UNKNOWN, "unassessed", self.world.clock.elapsed_seconds
                )
                self.reputations[self._reputation_key(f"public:{faction_id}", identity_id)] = ReputationVector(
                    f"public:{faction_id}", identity_id, updated_at=self.world.clock.elapsed_seconds
                )
        # Offices are intentionally assigned to NPCs, leaving player decisions
        # subject to institutional authority rather than privileged access.
        for index, faction_id in enumerate(self.definitions):
            npc_id = self.simulation.npc_ids[index % len(self.simulation.npc_ids)]
            self._assign_office(faction_id, npc_id, "COUNCIL_MEMBER", ["PROPOSE", "VOTE", "OPEN_CASE", "RECRUIT", "ISSUE_MISSION"])
            self._assign_office(faction_id, self.simulation.npc_ids[(index + 1) % len(self.simulation.npc_ids)], "SECURITY_OFFICER", ["INVESTIGATE", "VOTE", "WATCH", "ISSUE_MISSION"])
        for bloc in self.blocs.values():
            faction_members = [office.character_id for office in self.offices.values() if office.faction_id == bloc.faction_id]
            bloc.member_ids.extend(sorted(set(faction_members)))
            for member_id in bloc.member_ids:
                self.influence[self._influence_key(member_id, bloc.faction_id)] = InfluenceVector(
                    member_id, bloc.faction_id, formal_authority=20, information=20, prestige=10
                )

    def ingest_report(self, faction_id: str, member_id: str, report_id: str) -> InstitutionalBelief | None:
        self._require_member(faction_id, member_id)
        report = self.information.reports.get(report_id)
        if report is None or member_id not in report.delivered:
            return None
        beliefs = self.information.beliefs.get(member_id, {})
        changed: InstitutionalBelief | None = None
        for claim in report.claims:
            belief = beliefs.get(claim.hypothesis_id)
            if belief is None:
                continue
            key = self._institutional_key(faction_id, claim.hypothesis_id)
            existing = self.institutional_beliefs.get(key)
            groups = list(existing.origin_groups if existing else [])
            if report.independence_group_id not in groups:
                groups.append(report.independence_group_id)
            confidence = belief.confidence if existing is None else (existing.confidence + belief.confidence) // 2
            changed = InstitutionalBelief(
                faction_id,
                claim.hypothesis_id,
                confidence,
                sorted(set((existing.source_report_ids if existing else []) + [report_id])),
                groups,
                self.world.clock.elapsed_seconds,
                "ADOPTED" if confidence >= 70 else "DISPUTED",
            )
            self.institutional_beliefs[key] = changed
            self._emit("INSTITUTIONAL_BELIEF_UPDATED", member_id, faction_id, {"hypothesis_id": claim.hypothesis_id, "confidence": confidence})
        self._sync_world_state()
        return changed

    def open_case(
        self,
        faction_id: str,
        opener_id: str,
        subject_identity_id: str,
        hypothesis_ids: list[str],
        report_ids: list[str],
    ) -> FactionCase:
        self._require_authority(faction_id, opener_id, "OPEN_CASE")
        confidence = max(
            [
                self.institutional_beliefs.get(self._institutional_key(faction_id, hypothesis_id), InstitutionalBelief(faction_id, hypothesis_id, 0, [], [], 0)).confidence
                for hypothesis_id in hypothesis_ids
            ]
            or [0]
        )
        status = FactionCaseStatus.UNDER_INVESTIGATION if confidence >= B["case_open_threshold"] else FactionCaseStatus.RUMOR
        case_id = self._id("case")
        case = FactionCase(case_id, faction_id, subject_identity_id, hypothesis_ids, self.world.clock.elapsed_seconds, status, [], report_ids, None, confidence, ["OPEN_INVESTIGATION"], [{"event": "OPENED", "by": opener_id}])
        self.cases[case_id] = case
        self._emit("FACTION_CASE_OPENED", opener_id, faction_id, {"case_id": case_id, "status": status.value, "confidence": confidence})
        self._sync_world_state()
        return case

    def investigate_case(self, case_id: str, investigator_id: str, event_id: str) -> FactionCase:
        case = self.cases[case_id]
        self._require_authority(case.faction_id, investigator_id, "INVESTIGATE")
        case.assigned_investigator = investigator_id
        evidence = self.information.investigate_scene(investigator_id, event_id)
        if evidence:
            case.evidence_ids.append(evidence.evidence_id)
            case.history.append({"event": "EVIDENCE_FOUND", "evidence_id": evidence.evidence_id})
            case.institutional_confidence = max(
                [self.information.belief(investigator_id, hypothesis_id).confidence for hypothesis_id in case.hypothesis_ids if self.information.belief(investigator_id, hypothesis_id)]
                or [case.institutional_confidence]
            )
            case.status = FactionCaseStatus.CONFIRMED if case.institutional_confidence >= B["case_confirm_threshold"] else FactionCaseStatus.DISPUTED
        self._emit("FACTION_INVESTIGATION_RESULT", investigator_id, case.faction_id, {"case_id": case_id, "status": case.status.value})
        self._sync_world_state()
        return case

    def create_proposal(
        self,
        faction_id: str,
        proposer_id: str,
        proposal_type: FactionProposalType,
        *,
        target_identity_id: str | None = None,
        case_id: str | None = None,
        rationale: list[str] | None = None,
        cost: int = 0,
        risks: int = 0,
    ) -> FactionProposal:
        self._require_authority(faction_id, proposer_id, "PROPOSE")
        proposal = FactionProposal(self._id("proposal"), faction_id, proposal_type, proposer_id, target_identity_id, self.world.clock.elapsed_seconds, rationale or [], case_id, cost, risks)
        self.proposals[proposal.proposal_id] = proposal
        self._emit("FACTION_PROPOSAL_CREATED", proposer_id, faction_id, {"proposal_id": proposal.proposal_id, "type": proposal_type.value})
        self._sync_world_state()
        return proposal

    def evaluate_proposal(self, proposal_id: str) -> FactionProposal:
        proposal = self.proposals[proposal_id]
        office_holders = [office.character_id for office in self.offices.values() if office.faction_id == proposal.faction_id and office.active and "VOTE" in office.authority]
        for voter_id in sorted(set(office_holders)):
            office = next((office for office in self.offices.values() if office.character_id == voter_id and office.faction_id == proposal.faction_id), None)
            preferred_name = "SECURITY_HARDLINERS" if office and office.office_type == "SECURITY_OFFICER" else "TRADE_PRAGMATISTS"
            bloc = next((bloc for bloc in self.blocs.values() if bloc.name == preferred_name and bloc.faction_id == proposal.faction_id), None)
            need = max((need.intensity for need in self.needs.values() if need.faction_id == proposal.faction_id), default=0)
            security_bias = (bloc.priorities.get("SECURITY", 0) if bloc else 0)
            revenue_bias = (bloc.priorities.get("REVENUE", 0) if bloc else 0)
            risk_penalty = proposal.risks * max(0, 100 - (bloc.risk_tolerance if bloc else 50)) // 100
            score = need + security_bias + revenue_bias - proposal.cost - risk_penalty
            approve = score >= B["proposal_vote_threshold"]
            if proposal.proposal_type is FactionProposalType.RECRUIT_SUBJECT and bloc and "TRADE" in bloc.name:
                approve = True
                score += 10
            reason = "need_and_bloc_alignment" if approve else "risk_or_cost_exceeds_interest"
            proposal.votes.append(Vote(voter_id, bloc.bloc_id if bloc else None, approve, score, reason))
            self._emit("FACTION_VOTE_CAST", voter_id, proposal.faction_id, {"proposal_id": proposal_id, "approve": approve, "reason": reason})
        approved = sum(1 for vote in proposal.votes if vote.approve) > len(proposal.votes) / 2
        proposal.status = "APPROVED" if approved else "REJECTED"
        proposal.resolution = "majority_approved" if approved else "majority_rejected"
        if approved:
            self._apply_proposal(proposal)
        self._emit("FACTION_PROPOSAL_RESOLVED", proposal.proposer_id, proposal.faction_id, {"proposal_id": proposal_id, "status": proposal.status})
        self._sync_world_state()
        return proposal

    def recruit(self, faction_id: str, character_id: str, sponsor_id: str) -> Membership:
        self._require_authority(faction_id, sponsor_id, "RECRUIT")
        membership = self.memberships[self._membership_key(character_id, faction_id)]
        membership.status = MembershipStatus.AFFILIATE
        membership.joined_at = self.world.clock.elapsed_seconds
        membership.loyalty = min(100, membership.loyalty + B["recruitment_loyalty_gain"])
        membership.sponsor_id = sponsor_id
        identity = self._identity_for_character(character_id)
        self.standings[self._standing_key(faction_id, identity.identity_id)] = FactionStanding(faction_id, identity.identity_id, FactionStandingLevel.GUEST, "recruitment_offer", self.world.clock.elapsed_seconds)
        self._emit("MEMBERSHIP_CHANGED", sponsor_id, faction_id, {"character_id": character_id, "status": membership.status.value})
        self._sync_world_state()
        return membership

    def generate_mission(
        self,
        faction_id: str,
        issuer_id: str,
        objective_type: str = "INVESTIGATE",
        *,
        target_id: str | None = None,
        required_quantity: int = 1,
    ) -> FactionMission:
        self._require_authority(faction_id, issuer_id, "ISSUE_MISSION")
        need = max(
            self.needs.values(),
            key=lambda item: item.intensity if item.faction_id == faction_id else -1,
        )
        mission = FactionMission(
            self._id("mission"),
            faction_id,
            issuer_id,
            need.need_type,
            objective_type,
            target_id,
            20 + need.intensity // 2,
            self.world.clock.elapsed_seconds + B["mission_deadline_seconds"],
            ["OUTSIDER", "AFFILIATE", "MEMBER", "INNER_MEMBER", "ELDER"],
            required_quantity=max(1, required_quantity),
        )
        self.missions[mission.mission_id] = mission
        self._emit(
            "FACTION_MISSION_CREATED",
            issuer_id,
            faction_id,
            {
                "mission_id": mission.mission_id,
                "need_type": need.need_type,
                "objective_type": objective_type,
                "target_id": target_id,
                "required_quantity": mission.required_quantity,
            },
        )
        self._sync_world_state()
        return mission

    def accept_mission(self, mission_id: str, character_id: str) -> FactionMission:
        mission = self.missions[mission_id]
        if mission.status not in {"OPEN", "AVAILABLE"}:
            raise FactionValidationError("mission is not available")
        membership = self.memberships.get(self._membership_key(character_id, mission.faction_id))
        status = membership.status.value if membership else MembershipStatus.OUTSIDER.value
        if status not in mission.eligibility:
            raise FactionValidationError("character is not eligible for this mission")
        mission.status = "ACCEPTED"
        mission.assignee_id = character_id
        mission.accepted_at = self.world.clock.elapsed_seconds
        self._emit(
            "FACTION_MISSION_ACCEPTED",
            character_id,
            mission.faction_id,
            {"mission_id": mission_id},
        )
        self._sync_world_state()
        return mission

    def progress_mission(self, mission_id: str, character_id: str, amount: int = 1) -> FactionMission:
        mission = self.missions[mission_id]
        if mission.assignee_id != character_id or mission.status not in {"ACCEPTED", "IN_PROGRESS"}:
            raise FactionValidationError("character is not actively assigned to this mission")
        if amount <= 0:
            raise FactionValidationError("mission progress must be positive")
        mission.progress += amount
        mission.status = "IN_PROGRESS"
        self._emit(
            "FACTION_MISSION_PROGRESS",
            character_id,
            mission.faction_id,
            {
                "mission_id": mission_id,
                "progress": mission.progress,
                "required_quantity": mission.required_quantity,
            },
        )
        self._sync_world_state()
        return mission

    def complete_mission(self, mission_id: str, character_id: str) -> FactionMission:
        mission = self.missions[mission_id]
        if mission.assignee_id != character_id:
            raise FactionValidationError("mission is assigned to another character")
        if mission.progress < mission.required_quantity:
            raise FactionValidationError("mission objective is not complete")
        mission.status = "COMPLETED"
        mission.completed_at = self.world.clock.elapsed_seconds
        membership = self.memberships.get(self._membership_key(character_id, mission.faction_id))
        if membership:
            membership.contribution += mission.required_quantity
            membership.favor_balance += max(1, mission.required_quantity // 2)
        faction = self.states[mission.faction_id]
        payout = min(faction.treasury, mission.reward)
        faction.treasury -= payout
        self.simulation.characters[character_id].currency += payout
        self._emit(
            "FACTION_MISSION_COMPLETED",
            character_id,
            mission.faction_id,
            {
                "mission_id": mission_id,
                "reward": payout,
                "contribution": membership.contribution if membership else 0,
                "favor_balance": membership.favor_balance if membership else 0,
            },
        )
        self._sync_world_state()
        return mission

    def can_access_faction_warehouse(self, faction_id: str, character_id: str) -> bool:
        membership = self.memberships.get(self._membership_key(character_id, faction_id))
        if membership and membership.status not in {
            MembershipStatus.OUTSIDER,
            MembershipStatus.SUSPENDED,
            MembershipStatus.EXILED,
            MembershipStatus.TRAITOR,
        }:
            return True
        identity = self._identity_for_character(character_id)
        standing = self.standings.get(self._standing_key(faction_id, identity.identity_id))
        return bool(
            standing
            and standing.level
            in {
                FactionStandingLevel.GUEST,
                FactionStandingLevel.ALLY,
                FactionStandingLevel.MEMBER,
            }
        )

    def set_reputation(self, faction_id: str, identity_id: str, *, danger: int, trust: int, competence: int = 50) -> ReputationVector:
        audience = f"faction:{faction_id}"
        key = self._reputation_key(audience, identity_id)
        vector = self.reputations.get(key, ReputationVector(audience, identity_id))
        vector.danger = max(0, min(100, danger))
        vector.trust = max(0, min(100, trust))
        vector.competence = max(0, min(100, competence))
        vector.updated_at = self.world.clock.elapsed_seconds
        self.reputations[key] = vector
        self._sync_world_state()
        return vector

    def process_elapsed_time(self, seconds: int) -> None:
        """Apply coarse institutional consequences after the shared clock advances."""
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        now = self.world.clock.elapsed_seconds
        changed = False
        for mission in self.missions.values():
            if mission.status in {"OPEN", "AVAILABLE", "ACCEPTED", "IN_PROGRESS"} and mission.deadline <= now:
                previous = mission.status
                mission.status = "EXPIRED"
                self._emit(
                    "FACTION_MISSION_EXPIRED",
                    mission.issuer_id,
                    mission.faction_id,
                    {"mission_id": mission.mission_id, "status_before": previous},
                )
                changed = True
        for need in self.needs.values():
            need.updated_at = now
        if changed or self.needs:
            self._sync_world_state()

    def summary(self) -> dict[str, Any]:
        return {
            "factions": len(self.definitions),
            "memberships": len(self.memberships),
            "offices": len(self.offices),
            "blocs": len(self.blocs),
            "institutional_beliefs": len(self.institutional_beliefs),
            "cases": {key: value.status.value for key, value in self.cases.items()},
            "proposals": {key: value.status for key, value in self.proposals.items()},
            "missions": len(self.missions),
            "standings": {key: value.level.value for key, value in self.standings.items() if value.level is not FactionStandingLevel.UNKNOWN},
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "m4_schema_version": self.M4_SCHEMA_VERSION,
            "definitions": {key: value.to_dict() for key, value in self.definitions.items()},
            "states": {key: value.to_dict() for key, value in self.states.items()},
            "needs": {key: value.to_dict() for key, value in self.needs.items()},
            "memberships": {key: value.to_dict() for key, value in self.memberships.items()},
            "offices": {key: value.to_dict() for key, value in self.offices.items()},
            "blocs": {key: value.to_dict() for key, value in self.blocs.items()},
            "institutional_beliefs": {key: value.to_dict() for key, value in self.institutional_beliefs.items()},
            "identities": {key: value.to_dict() for key, value in self.identities.items()},
            "reputations": {key: value.to_dict() for key, value in self.reputations.items()},
            "standings": {key: value.to_dict() for key, value in self.standings.items()},
            "cases": {key: value.to_dict() for key, value in self.cases.items()},
            "proposals": {key: value.to_dict() for key, value in self.proposals.items()},
            "influence": {key: value.to_dict() for key, value in self.influence.items()},
            "missions": {key: value.to_dict() for key, value in self.missions.items()},
            "sequence": self._sequence,
        }

    def _load_dict(self, data: dict[str, Any]) -> None:
        self.definitions = {key: FactionDefinition.from_dict(value) for key, value in data.get("definitions", {}).items()}
        self.states = {key: FactionState.from_dict(value) for key, value in data.get("states", {}).items()}
        self.needs = {key: FactionNeed.from_dict(value) for key, value in data.get("needs", {}).items()}
        self.memberships = {key: Membership.from_dict(value) for key, value in data.get("memberships", {}).items()}
        self.offices = {key: OfficeAssignment.from_dict(value) for key, value in data.get("offices", {}).items()}
        self.blocs = {key: PoliticalBloc.from_dict(value) for key, value in data.get("blocs", {}).items()}
        self.institutional_beliefs = {key: InstitutionalBelief.from_dict(value) for key, value in data.get("institutional_beliefs", {}).items()}
        self.identities = {key: SocialIdentity.from_dict(value) for key, value in data.get("identities", {}).items()}
        self.reputations = {key: ReputationVector.from_dict(value) for key, value in data.get("reputations", {}).items()}
        self.standings = {key: FactionStanding.from_dict(value) for key, value in data.get("standings", {}).items()}
        self.cases = {key: FactionCase.from_dict(value) for key, value in data.get("cases", {}).items()}
        self.proposals = {key: FactionProposal.from_dict(value) for key, value in data.get("proposals", {}).items()}
        self.influence = {key: InfluenceVector.from_dict(value) for key, value in data.get("influence", {}).items()}
        self.missions = {key: FactionMission.from_dict(value) for key, value in data.get("missions", {}).items()}
        self._sequence = int(data.get("sequence", 0))

    def _apply_proposal(self, proposal: FactionProposal) -> None:
        if proposal.target_identity_id is None:
            return
        standing = self.standings.get(self._standing_key(proposal.faction_id, proposal.target_identity_id))
        if standing is None:
            standing = FactionStanding(proposal.faction_id, proposal.target_identity_id, FactionStandingLevel.UNKNOWN, "", self.world.clock.elapsed_seconds)
            self.standings[self._standing_key(proposal.faction_id, proposal.target_identity_id)] = standing
        if proposal.proposal_type in {FactionProposalType.WATCH_SUBJECT, FactionProposalType.OPEN_INVESTIGATION}:
            standing.level = FactionStandingLevel.WATCHED
            standing.reason = "institutional_watch"
        elif proposal.proposal_type in {FactionProposalType.SANCTION_SUBJECT, FactionProposalType.RESTRICT_ACCESS}:
            standing.level = FactionStandingLevel.SUSPICIOUS
            standing.reason = "institutional_sanction"
        elif proposal.proposal_type in {FactionProposalType.RECRUIT_SUBJECT, FactionProposalType.OFFER_AFFILIATION}:
            standing.level = FactionStandingLevel.GUEST
            standing.reason = "institutional_recruitment"
        elif proposal.proposal_type is FactionProposalType.CLOSE_CASE:
            standing.level = FactionStandingLevel.NEUTRAL
            standing.reason = "case_closed"
        standing.updated_at = self.world.clock.elapsed_seconds
        self._emit("FACTION_STANDING_CHANGED", proposal.proposer_id, proposal.faction_id, {"identity_id": proposal.target_identity_id, "level": standing.level.value})

    def _assign_office(self, faction_id: str, character_id: str, office_type: str, authority: list[str]) -> OfficeAssignment:
        assignment = OfficeAssignment(self._id("office"), faction_id, character_id, office_type, authority, self.world.clock.elapsed_seconds)
        self.offices[assignment.assignment_id] = assignment
        membership = self.memberships[self._membership_key(character_id, faction_id)]
        membership.status = MembershipStatus.ELDER
        membership.privileges.extend(authority)
        return assignment

    def _require_member(self, faction_id: str, character_id: str) -> None:
        membership = self.memberships.get(self._membership_key(character_id, faction_id))
        if membership is None or membership.status in {MembershipStatus.OUTSIDER, MembershipStatus.EXILED, MembershipStatus.TRAITOR}:
            raise FactionValidationError("character is not an authorized faction member")

    def _require_authority(self, faction_id: str, character_id: str, capability: str) -> None:
        self._require_member(faction_id, character_id)
        if not any(office.faction_id == faction_id and office.character_id == character_id and capability in office.authority and office.active for office in self.offices.values()):
            raise FactionValidationError(f"character lacks faction authority: {capability}")

    def _identity_for_character(self, character_id: str) -> SocialIdentity:
        return next(identity for identity in self.identities.values() if identity.character_id == character_id and identity.is_real_identity is False)

    def _emit(self, event_type: str, actor_id: str | None, faction_id: str, payload: dict[str, Any]) -> None:
        from ..core.events import DomainEvent
        event = DomainEvent(
            event_id=self.world.entity_ids.next("event"), event_type=event_type, timestamp=self.world.clock.elapsed_seconds,
            actor_id=actor_id, location_id=self.definitions[faction_id].headquarters_location_id,
            payload={**payload, "faction_id": faction_id}, source="M4_FACTION", provenance="GAME_EXTENSION",
        )
        self.event_bus.publish(event)
        self.event_bus.dispatch_pending()

    def _sync_world_state(self) -> None:
        self.simulation._sync_world_state()
        self.world.game_state["m4_factions"] = self.to_dict()

    def _id(self, prefix: str) -> str:
        self._sequence += 1
        return self.world.entity_ids.next(prefix)

    @staticmethod
    def _membership_key(character_id: str, faction_id: str) -> str:
        return f"{character_id}::{faction_id}"

    @staticmethod
    def _standing_key(faction_id: str, identity_id: str) -> str:
        return f"{faction_id}::{identity_id}"

    @staticmethod
    def _reputation_key(audience_id: str, identity_id: str) -> str:
        return f"{audience_id}::{identity_id}"

    @staticmethod
    def _institutional_key(faction_id: str, hypothesis_id: str) -> str:
        return f"{faction_id}::{hypothesis_id}"

    @staticmethod
    def _influence_key(character_id: str, faction_id: str) -> str:
        return f"{character_id}::{faction_id}"
