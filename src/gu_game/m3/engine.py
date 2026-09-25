"""Deterministic information, memory, relationship and rumor engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..core.events import DomainEvent
from ..m1.simulation import Simulation
from ..provenance import Provenance
from ..save import load_world, save_world
from .balance import GAME_EXTENSION_INFORMATION_BALANCE as B
from .models import (
    BasisType,
    BeliefRecord,
    CertaintyClass,
    Channel,
    EvidenceItem,
    EvidenceSupport,
    Hypothesis,
    InformationDecision,
    InformationReport,
    MemoryRecord,
    Observation,
    RelationshipState,
    ReportClaim,
    ReportIntention,
    RumorThread,
    SourceProfile,
    Transmission,
)


class InformationValidationError(ValueError):
    """Raised when an information action violates a deterministic rule."""


class InformationEngine:
    """WorldTruth-aware engine whose NPC-facing state is belief-only."""

    M3_SCHEMA_VERSION = 1

    def __init__(self, simulation: Simulation) -> None:
        self.simulation = simulation
        self.world = simulation.world
        self.event_bus = simulation.event_bus
        self.hypotheses: dict[str, Hypothesis] = {}
        self.observations: dict[str, Observation] = {}
        self.evidence: dict[str, EvidenceItem] = {}
        self.reports: dict[str, InformationReport] = {}
        self.source_profiles: dict[str, SourceProfile] = {}
        self.beliefs: dict[str, dict[str, BeliefRecord]] = {}
        self.memories: dict[str, list[MemoryRecord]] = {}
        self.relationships: dict[str, RelationshipState] = {}
        self.rumors: dict[str, RumorThread] = {}
        self.transmissions: list[Transmission] = []
        self.investigations: dict[str, dict[str, Any]] = {}
        self._sequence = 0

    @classmethod
    def new(cls, simulation: Simulation) -> "InformationEngine":
        return cls(simulation)

    @classmethod
    def from_simulation(cls, simulation: Simulation) -> "InformationEngine":
        engine = cls(simulation)
        data = simulation.world.game_state.get("m3_information")
        if data:
            engine._load_dict(data)
        return engine

    @classmethod
    def load(cls, path: str | Path) -> "InformationEngine":
        world = load_world(path)
        return cls.from_simulation(Simulation.from_world_state(world))

    def save(self, path: str | Path) -> Path:
        self._sync_world_state()
        return save_world(self.world, path)

    def register_hypothesis(
        self,
        hypothesis_id: str,
        subject_id: str,
        predicate: str,
        object_value: Any,
        parameters: dict[str, Any] | None = None,
    ) -> Hypothesis:
        hypothesis = Hypothesis(hypothesis_id, subject_id, predicate, object_value, parameters or {})
        self.hypotheses[hypothesis_id] = hypothesis
        return hypothesis

    def set_source_profile(
        self,
        evaluator_id: str,
        source_id: str,
        *,
        trustworthiness: int = 50,
        domain_expertise: int = 50,
        honesty_history: int = 50,
        relationship_bias: int = 0,
        motive_modifier: int = 0,
    ) -> SourceProfile:
        profile = SourceProfile(
            evaluator_id=evaluator_id,
            source_id=source_id,
            trustworthiness=trustworthiness,
            domain_expertise=domain_expertise,
            honesty_history=honesty_history,
            relationship_bias=relationship_bias,
            motive_modifier=motive_modifier,
            last_updated=self.world.clock.elapsed_seconds,
        )
        self.source_profiles[self._source_key(evaluator_id, source_id)] = profile
        return profile

    def observe_event(
        self,
        observer_id: str,
        event_id: str,
        *,
        distance: int = 0,
        sensory_basis: str = "VISUAL",
    ) -> Observation | None:
        event = self._event(event_id)
        observer = self._character(observer_id)
        if event.location_id and observer.location_id != event.location_id:
            return None
        if distance > B["observation_distance_limit"]:
            return None
        features: dict[str, Any] = {"event_type": event.event_type}
        if event.actor_id:
            features["visible_actor_id"] = event.actor_id
        if event.target_ids:
            features["visible_target_count"] = len(event.target_ids)
        if event.event_type in {"ATTACK_HIT", "INJURY_APPLIED", "FLEE_ATTEMPTED"}:
            if event.payload.get("body_part"):
                features["coarse_body_part"] = event.payload["body_part"]
            if event.payload.get("position_after") is not None:
                features["movement_occurred"] = True
        if event.event_type == "COMBAT_STARTED":
            features["combat_present"] = True
        quality = max(20, B["observation_base_quality"] - distance * 5)
        observation = Observation(
            observation_id=self._id("observation"),
            observer_id=observer_id,
            event_id=event_id,
            location_id=event.location_id or observer.location_id,
            observed_at=self.world.clock.elapsed_seconds,
            observation_type="DIRECT_EVENT",
            perceived_features=features,
            quality=quality,
            confidence=quality,
            sensory_basis=sensory_basis,
        )
        self.observations[observation.observation_id] = observation
        salience = (
            B["violence_memory_salience"]
            if event.event_type in {"ATTACK_HIT", "INJURY_APPLIED", "COMBAT_ENDED"}
            else B["gossip_memory_salience"]
        )
        self._remember(
            observer_id,
            event_id=event_id,
            observation_id=observation.observation_id,
            memory_type="DIRECT_OBSERVATION",
            salience=salience,
            emotional_tags=["FEAR"] if salience >= 80 else ["CURIOSITY"],
            persistence=salience,
        )
        self._emit(
            "OBSERVATION_CREATED",
            actor_id=observer_id,
            location_id=observation.location_id,
            payload={
                "observation_id": observation.observation_id,
                "event_id": event_id,
                "features": features,
                "quality": quality,
                "privacy_boundary": "INCOMPLETE_PERCEPTION",
            },
        )
        self._sync_world_state()
        return observation

    def create_evidence(
        self,
        observer_id: str,
        observation_id: str,
        *,
        evidence_type: str,
        supports: list[tuple[str, int, int]],
        independence_group_id: str | None = None,
    ) -> EvidenceItem:
        observation = self.observations[observation_id]
        group = independence_group_id or f"evidence-group-{observation_id}"
        item = EvidenceItem(
            evidence_id=self._id("evidence"),
            evidence_type=evidence_type,
            origin_event_id=observation.event_id,
            origin_observation_id=observation_id,
            location_id=observation.location_id,
            holder_id=observer_id,
            created_at=self.world.clock.elapsed_seconds,
            quality=observation.quality,
            authenticity=100,
            tampered=False,
            independence_group_id=group,
            supports=[
                EvidenceSupport(item_id, hypothesis_id, support, contradiction)
                for hypothesis_id, support, contradiction in supports
                for item_id in [self._peek_id("evidence")]
            ],
        )
        # The comprehension above uses the generated evidence id for each relation.
        self.evidence[item.evidence_id] = item
        observation.evidence_ids.append(item.evidence_id)
        self._apply_evidence(observer_id, item)
        self._emit(
            "EVIDENCE_DISCOVERED",
            actor_id=observer_id,
            location_id=item.location_id,
            payload={
                "evidence_id": item.evidence_id,
                "evidence_type": evidence_type,
                "origin_observation_id": observation_id,
                "independence_group_id": group,
            },
        )
        self._sync_world_state()
        return item

    def create_report(
        self,
        sender_id: str,
        receiver_id: str | None,
        claims: list[ReportClaim | dict[str, Any]],
        *,
        channel: Channel = Channel.FACE_TO_FACE,
        claimed_basis: BasisType = BasisType.FIRST_HAND,
        actual_basis: BasisType | None = None,
        asserted_confidence: int = 70,
        evidence_references: list[str] | None = None,
        intention: ReportIntention = ReportIntention.INFORM,
        parent_report_id: str | None = None,
        origin_chain_id: str | None = None,
        independence_group_id: str | None = None,
    ) -> InformationReport:
        normalized = [
            item if isinstance(item, ReportClaim) else ReportClaim.from_dict(item)
            for item in claims
        ]
        parent = self.reports.get(parent_report_id or "")
        report = InformationReport(
            report_id=self._id("report"),
            sender_id=sender_id,
            receiver_id=receiver_id,
            audience=[receiver_id] if receiver_id else [],
            created_at=self.world.clock.elapsed_seconds,
            source_type=channel,
            claims=normalized,
            claimed_basis=claimed_basis,
            actual_basis=actual_basis or claimed_basis,
            asserted_confidence=max(0, min(100, asserted_confidence)),
            evidence_references=list(evidence_references or []),
            intention=intention,
            transmission_quality=self._channel_quality(channel),
            parent_report_id=parent_report_id,
            origin_chain_id=origin_chain_id or (parent.origin_chain_id if parent else self._id("origin-chain")),
            independence_group_id=independence_group_id or (parent.independence_group_id if parent else self._id("independence")),
        )
        self.reports[report.report_id] = report
        self._emit(
            "REPORT_CREATED",
            actor_id=sender_id,
            target_ids=tuple(report.audience),
            payload={
                "report_id": report.report_id,
                "claimed_basis": claimed_basis.value,
                "actual_basis_internal": actual_basis.value if actual_basis else claimed_basis.value,
                "intention": intention.value,
                "origin_chain_id": report.origin_chain_id,
                "independence_group_id": report.independence_group_id,
            },
        )
        if receiver_id:
            self._queue_report(report, receiver_id)
        self._sync_world_state()
        return report

    def create_rumor(
        self,
        origin_report_id: str,
        receiver_id: str,
        *,
        channel: Channel = Channel.MARKET_GOSSIP,
        semantic_slots: dict[str, Any] | None = None,
    ) -> RumorThread:
        report = self.reports[origin_report_id]
        first_hypothesis = report.claims[0].hypothesis_id
        parent_rumor = next(
            (
                item
                for item in self.rumors.values()
                if self._root_report_id(item.origin_report_id) == self._root_report_id(origin_report_id)
            ),
            None,
        )
        inherited_slots = dict(parent_rumor.semantic_slots) if parent_rumor else {}
        rumor = RumorThread(
            rumor_id=self._id("rumor"),
            primary_hypothesis_id=first_hypothesis,
            origin_report_id=origin_report_id,
            origin_chain_id=report.origin_chain_id,
            created_at=self.world.clock.elapsed_seconds,
            origin_location_id=self._character(report.sender_id).location_id,
            current_locations=[self._character(report.sender_id).location_id],
            spread_strength=report.asserted_confidence,
            mutation_level=(parent_rumor.mutation_level + 1) if parent_rumor else 1,
            public_visibility=report.asserted_confidence,
            semantic_slots=dict(semantic_slots or inherited_slots),
        )
        self.rumors[rumor.rumor_id] = rumor
        self._queue_report(report, receiver_id, mutation_level=rumor.mutation_level)
        self._emit(
            "RUMOR_CREATED",
            actor_id=report.sender_id,
            target_ids=(receiver_id,),
            payload={"rumor_id": rumor.rumor_id, "origin_report_id": origin_report_id},
        )
        self._sync_world_state()
        return rumor

    def advance_time(self, seconds: int) -> None:
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        self.world.clock.advance(seconds)
        self._decay_beliefs(seconds)
        due = sorted(
            [item for item in self.transmissions if item.deliver_at <= self.world.clock.elapsed_seconds],
            key=lambda item: (item.deliver_at, item.sequence),
        )
        for transmission in due:
            if transmission in self.transmissions:
                self.transmissions.remove(transmission)
            self._deliver_transmission(transmission)
        self._sync_world_state()

    def investigate_scene(
        self,
        investigator_id: str,
        event_id: str,
        supports: list[tuple[str, int, int]] | None = None,
    ) -> EvidenceItem | None:
        investigation_id = self._id("investigation")
        self._emit(
            "INVESTIGATION_STARTED",
            actor_id=investigator_id,
            payload={"investigation_id": investigation_id, "event_id": event_id},
        )
        observation = self.observe_event(investigator_id, event_id, sensory_basis="SCENE_INSPECTION")
        if observation is None:
            self._emit(
                "INVESTIGATION_RESULT",
                actor_id=investigator_id,
                payload={"investigation_id": investigation_id, "result": "NO_ACCESS"},
            )
            return None
        evidence = self.create_evidence(
            investigator_id,
            observation.observation_id,
            evidence_type="PHYSICAL_TRACE",
            supports=supports or self.investigation_supports(event_id, list(self.hypotheses)),
            independence_group_id=f"investigation-{investigation_id}",
        )
        self._emit(
            "INVESTIGATION_RESULT",
            actor_id=investigator_id,
            payload={"investigation_id": investigation_id, "evidence_id": evidence.evidence_id},
        )
        return evidence

    def investigation_supports(
        self, event_id: str, hypothesis_ids: list[str]
    ) -> list[tuple[str, int, int]]:
        """Derive evidence relations from observable event traces.

        This is a small deterministic rule table, not a truth-reveal API. The
        caller gets only relations that the registered trace rule can justify.
        """

        event = self._event(event_id)
        relations: list[tuple[str, int, int]] = []
        for hypothesis_id in hypothesis_ids:
            hypothesis = self.hypotheses[hypothesis_id]
            if event.event_type in {"ATTACK_HIT", "INJURY_APPLIED"}:
                if hypothesis.predicate == "initiated_attack":
                    if hypothesis.subject_id == event.actor_id and hypothesis.object_value is True:
                        relations.append((hypothesis_id, 45, 0))
                    elif hypothesis.subject_id in event.target_ids and hypothesis.object_value is True:
                        relations.append((hypothesis_id, 0, 45))
                elif hypothesis.predicate == "dangerous" and hypothesis.object_value is True:
                    if hypothesis.subject_id in event.target_ids:
                        relations.append((hypothesis_id, 0, 30))
        return relations

    def decide(self, actor_id: str, target_id: str, hypothesis_id: str) -> InformationDecision:
        belief = self.beliefs.get(actor_id, {}).get(hypothesis_id)
        confidence = belief.confidence if belief else 50
        if confidence >= B["decision_avoid_threshold"]:
            action, reason = "AVOID_TARGET", "belief_confidence_high"
        elif confidence <= B["decision_approach_threshold"]:
            action, reason = "APPROACH_TARGET", "belief_confidence_low"
        else:
            action, reason = "ASK", "belief_uncertain"
        decision = InformationDecision(actor_id, target_id, action, reason, confidence)
        self._emit(
            "INFORMATION_ACTION_SELECTED",
            actor_id=actor_id,
            target_ids=(target_id,),
            payload=decision.to_dict() | {"hypothesis_id": hypothesis_id},
        )
        return decision

    def belief(self, character_id: str, hypothesis_id: str) -> BeliefRecord | None:
        return self.beliefs.get(character_id, {}).get(hypothesis_id)

    def relationship(self, source_id: str, target_id: str) -> RelationshipState:
        key = self._relationship_key(source_id, target_id)
        if key not in self.relationships:
            self.relationships[key] = RelationshipState(source_id, target_id, last_updated=self.world.clock.elapsed_seconds)
        return self.relationships[key]

    def to_dict(self) -> dict[str, Any]:
        return {
            "m3_schema_version": self.M3_SCHEMA_VERSION,
            "hypotheses": {key: value.to_dict() for key, value in sorted(self.hypotheses.items())},
            "observations": {key: value.to_dict() for key, value in sorted(self.observations.items())},
            "evidence": {key: value.to_dict() for key, value in sorted(self.evidence.items())},
            "reports": {key: value.to_dict() for key, value in sorted(self.reports.items())},
            "source_profiles": {key: value.to_dict() for key, value in sorted(self.source_profiles.items())},
            "beliefs": {
                character: {key: value.to_dict() for key, value in sorted(records.items())}
                for character, records in sorted(self.beliefs.items())
            },
            "memories": {
                character: [item.to_dict() for item in records]
                for character, records in sorted(self.memories.items())
            },
            "relationships": {key: value.to_dict() for key, value in sorted(self.relationships.items())},
            "rumors": {key: value.to_dict() for key, value in sorted(self.rumors.items())},
            "transmissions": [item.to_dict() for item in sorted(self.transmissions, key=lambda item: (item.deliver_at, item.sequence))],
            "investigations": self.investigations,
            "sequence": self._sequence,
        }

    def _load_dict(self, data: dict[str, Any]) -> None:
        self.hypotheses = {key: Hypothesis.from_dict(value) for key, value in data.get("hypotheses", {}).items()}
        self.observations = {key: Observation.from_dict(value) for key, value in data.get("observations", {}).items()}
        self.evidence = {key: EvidenceItem.from_dict(value) for key, value in data.get("evidence", {}).items()}
        self.reports = {key: InformationReport.from_dict(value) for key, value in data.get("reports", {}).items()}
        self.source_profiles = {key: SourceProfile.from_dict(value) for key, value in data.get("source_profiles", {}).items()}
        self.beliefs = {
            character: {key: BeliefRecord.from_dict(value) for key, value in records.items()}
            for character, records in data.get("beliefs", {}).items()
        }
        self.memories = {
            character: [MemoryRecord.from_dict(item) for item in records]
            for character, records in data.get("memories", {}).items()
        }
        self.relationships = {key: RelationshipState.from_dict(value) for key, value in data.get("relationships", {}).items()}
        self.rumors = {key: RumorThread.from_dict(value) for key, value in data.get("rumors", {}).items()}
        self.transmissions = [Transmission.from_dict(item) for item in data.get("transmissions", [])]
        self.investigations = dict(data.get("investigations", {}))
        self._sequence = int(data.get("sequence", 0))

    def _apply_evidence(self, evaluator_id: str, evidence: EvidenceItem) -> None:
        for support in evidence.supports:
            record = self._belief_record(evaluator_id, support.hypothesis_id, category="IMMEDIATE")
            record.category = "IMMEDIATE"
            if evidence.independence_group_id not in record.origin_groups_seen:
                delta = support.support_strength - support.contradiction_strength + B["independent_evidence_bonus"]
                record.origin_groups_seen.append(evidence.independence_group_id)
            else:
                delta = (support.support_strength - support.contradiction_strength) // B["correlated_source_divisor"]
            record.confidence = max(0, min(100, record.confidence + delta))
            if support.support_strength >= support.contradiction_strength:
                record.supporting_evidence_ids.append(evidence.evidence_id)
            else:
                record.contradicting_evidence_ids.append(evidence.evidence_id)
            record.last_updated = self.world.clock.elapsed_seconds
            record.refresh_class()
            self._emit_belief_update(evaluator_id, record, "evidence")
            self._update_source_credibility_from_evidence(evaluator_id, record, support)

    def _deliver_transmission(self, transmission: Transmission) -> None:
        report = self.reports[transmission.report_id]
        if transmission.mutation_level:
            self._mutate_rumor(report, transmission.mutation_level)
            interpreted = self._derive_mutated_report(report, transmission)
            if interpreted is not None:
                self._deliver_report(interpreted, transmission.receiver_id)
                self._emit(
                    "REPORT_DELIVERED",
                    actor_id=report.sender_id,
                    target_ids=(transmission.receiver_id,),
                    payload={"report_id": interpreted.report_id, "parent_report_id": report.report_id, "channel": transmission.channel.value, "origin_chain_id": report.origin_chain_id},
                )
                return
        if transmission.receiver_id not in report.delivered:
            report.delivered.add(transmission.receiver_id)
            self._deliver_report(report, transmission.receiver_id)
            self._emit(
                "REPORT_DELIVERED",
                actor_id=report.sender_id,
                target_ids=(transmission.receiver_id,),
                payload={"report_id": report.report_id, "channel": transmission.channel.value, "origin_chain_id": report.origin_chain_id},
            )

    def _deliver_report(self, report: InformationReport, receiver_id: str) -> None:
        credibility_scores: list[int] = []
        for claim in report.claims:
            record = self._belief_record(receiver_id, claim.hypothesis_id, category="RUMOR")
            credibility = self._credibility_score(receiver_id, report, claim)
            credibility_scores.append(credibility)
            gain = max(1, credibility * claim.asserted_confidence // 100)
            if report.independence_group_id in record.origin_groups_seen:
                gain //= B["correlated_source_divisor"]
            else:
                record.origin_groups_seen.append(report.independence_group_id)
            if claim.supports:
                record.confidence = min(100, record.confidence + gain)
                record.supporting_evidence_ids.extend(report.evidence_references)
            else:
                record.confidence = max(0, record.confidence - gain)
                record.contradicting_evidence_ids.extend(report.evidence_references)
            record.report_ids.append(report.report_id)
            record.last_updated = self.world.clock.elapsed_seconds
            record.refresh_class()
            self._emit_belief_update(receiver_id, record, "report")
        self._remember(
            receiver_id,
            event_id=None,
            observation_id=None,
            report_id=report.report_id,
            memory_type="REPORTED_EVENT",
            salience=max(20, report.asserted_confidence),
            emotional_tags=["FEAR"] if report.intention is ReportIntention.WARN else ["CURIOSITY"],
            persistence=max(30, report.asserted_confidence // 2),
        )
        # RelationshipState(source_id -> target_id) is directional. Receiving
        # a credible report changes the receiver's view of the sender.
        relationship = self.relationship(receiver_id, report.sender_id)
        average_credibility = sum(credibility_scores) // max(1, len(credibility_scores))
        if average_credibility >= 70:
            relationship.trust = max(
                0, min(100, relationship.trust + B["relationship_trust_report_delta"])
            )
        elif average_credibility <= 35:
            relationship.trust = max(0, relationship.trust - 1)
        relationship.last_updated = self.world.clock.elapsed_seconds
        self._emit(
            "RELATIONSHIP_CHANGED",
            actor_id=receiver_id,
            target_ids=(report.sender_id,),
            payload={"trust": relationship.trust, "reason": "received_report"},
        )

    def _credibility_score(
        self, evaluator_id: str, report: InformationReport, claim: ReportClaim
    ) -> int:
        """Return deterministic receiver-specific report credibility.

        Actual basis is intentionally excluded: a receiver cannot use hidden
        lie metadata before discovering an inconsistency.
        """

        profile = self.source_profiles.get(
            self._source_key(evaluator_id, report.sender_id),
            SourceProfile(evaluator_id, report.sender_id),
        )
        relationship = self.relationship(evaluator_id, report.sender_id)
        basis_bonus = {
            BasisType.FIRST_HAND: B["first_hand_gain"],
            BasisType.SECOND_HAND: B["second_hand_gain"],
            BasisType.DELIBERATE_LIE: B["deliberate_lie_gain"],
            BasisType.INFERRED: 8,
        }[report.claimed_basis]
        weighted = (
            claim.asserted_confidence * 25
            + report.transmission_quality * 15
            + profile.trustworthiness * 15
            + profile.domain_expertise * 10
            + profile.honesty_history * 15
            + relationship.trust * 10
            + max(0, relationship.respect) * 5
        ) // 100
        return max(
            1,
            min(
                100,
                weighted
                + basis_bonus
                + profile.relationship_bias
                + profile.motive_modifier
                - relationship.fear // 4
                - relationship.resentment // 4,
            ),
        )

    def _update_source_credibility_from_evidence(
        self, evaluator_id: str, belief: BeliefRecord, support: EvidenceSupport
    ) -> None:
        evidence_supports_hypothesis = support.support_strength >= support.contradiction_strength
        for report_id in belief.report_ids:
            report = self.reports.get(report_id)
            if report is None:
                continue
            matching_claims = [claim for claim in report.claims if claim.hypothesis_id == support.hypothesis_id]
            # Only a report whose polarity conflicts with the new evidence is
            # actually contradicted. Corroborated claims are never penalized.
            if not matching_claims or all(claim.supports == evidence_supports_hypothesis for claim in matching_claims):
                continue
            key = self._source_key(evaluator_id, report.sender_id)
            profile = self.source_profiles.get(key)
            if profile is None:
                profile = SourceProfile(evaluator_id, report.sender_id)
                self.source_profiles[key] = profile
            profile.trustworthiness = max(0, profile.trustworthiness - 12)
            profile.honesty_history = max(0, profile.honesty_history - 15)
            profile.last_updated = self.world.clock.elapsed_seconds
            self._emit(
                "SOURCE_CREDIBILITY_UPDATED",
                actor_id=evaluator_id,
                target_ids=(report.sender_id,),
                payload={
                    "source_id": report.sender_id,
                    "trustworthiness": profile.trustworthiness,
                    "honesty_history": profile.honesty_history,
                    "reason": "contradictory_independent_evidence",
                },
            )

    def _mutate_rumor(self, report: InformationReport, mutation_level: int) -> None:
        for rumor in self.rumors.values():
            if self._root_report_id(report.report_id) != self._root_report_id(rumor.origin_report_id):
                continue
            if mutation_level % 2 == 1 and "initiator" in rumor.semantic_slots:
                rumor.semantic_slots["initiator"] = "unknown-third-party"
                rumor.mutation_level += 1
                self._emit(
                    "RUMOR_MUTATED",
                    actor_id=report.sender_id,
                    payload={"rumor_id": rumor.rumor_id, "semantic_slots": rumor.semantic_slots.copy(), "origin_chain_id": rumor.origin_chain_id},
                )
            self._emit(
                "RUMOR_SPREAD",
                actor_id=report.sender_id,
                payload={"rumor_id": rumor.rumor_id, "origin_chain_id": rumor.origin_chain_id},
            )

    def _derive_mutated_report(
        self, report: InformationReport, transmission: Transmission
    ) -> InformationReport | None:
        if transmission.mutation_level <= 0:
            return None
        rumor = next(
            (
                item
                for item in self.rumors.values()
                if self._root_report_id(item.origin_report_id) == self._root_report_id(report.report_id)
            ),
            None,
        )
        if rumor is None or rumor.semantic_slots.get("initiator") != "unknown-third-party":
            return None
        derived_claims: list[ReportClaim] = []
        for claim in report.claims:
            hypothesis = self.hypotheses.get(claim.hypothesis_id)
            if hypothesis and hypothesis.predicate == "initiated_attack":
                derived_id = f"derived:{rumor.rumor_id}:{claim.hypothesis_id}"
                if derived_id not in self.hypotheses:
                    self.register_hypothesis(
                        derived_id,
                        "unknown-third-party",
                        hypothesis.predicate,
                        hypothesis.object_value,
                        {"parent_hypothesis_id": hypothesis.hypothesis_id, "origin_chain_id": report.origin_chain_id},
                    )
                derived_claims.append(
                    ReportClaim(derived_id, "unknown-third-party", claim.supports, claim.asserted_confidence)
                )
            else:
                derived_claims.append(claim)
        derived_id = self._id("derived-report")
        derived = InformationReport(
            report_id=derived_id,
            sender_id=report.sender_id,
            receiver_id=transmission.receiver_id,
            audience=[transmission.receiver_id],
            created_at=self.world.clock.elapsed_seconds,
            source_type=report.source_type,
            claims=derived_claims,
            claimed_basis=report.claimed_basis,
            actual_basis=report.actual_basis,
            asserted_confidence=report.asserted_confidence,
            evidence_references=list(report.evidence_references),
            intention=report.intention,
            transmission_quality=report.transmission_quality,
            parent_report_id=report.report_id,
            origin_chain_id=report.origin_chain_id,
            independence_group_id=report.independence_group_id,
        )
        self.reports[derived.report_id] = derived
        return derived

    def _queue_report(self, report: InformationReport, receiver_id: str, mutation_level: int = 0) -> None:
        delay = self._channel_delay(report.source_type)
        self._sequence += 1
        self.transmissions.append(
            Transmission(
                transmission_id=self._id("transmission"),
                report_id=report.report_id,
                receiver_id=receiver_id,
                deliver_at=self.world.clock.elapsed_seconds + delay,
                channel=report.source_type,
                mutation_level=mutation_level,
                sequence=self._sequence,
            )
        )

    def _decay_beliefs(self, seconds: int) -> None:
        hours = seconds // 3_600
        if hours <= 0:
            return
        for character_id, records in self.beliefs.items():
            for record in records.values():
                decay = B["immediate_decay_per_hour"] if record.category == "IMMEDIATE" else B["rumor_decay_per_hour"]
                if record.confidence > 50:
                    record.confidence = max(50, record.confidence - decay * hours)
                elif record.confidence < 50:
                    record.confidence = min(50, record.confidence + decay * hours)
                record.last_updated = self.world.clock.elapsed_seconds
                record.refresh_class()
                self._emit_belief_update(character_id, record, "decay")

    def _belief_record(self, character_id: str, hypothesis_id: str, *, category: str) -> BeliefRecord:
        store = self.beliefs.setdefault(character_id, {})
        if hypothesis_id not in store:
            store[hypothesis_id] = BeliefRecord(hypothesis_id=hypothesis_id, category=category)
        elif category == "IMMEDIATE":
            # Strong/current evidence upgrades a rumor-origin belief; it does
            # not remain subject to rumor decay merely because rumor arrived first.
            store[hypothesis_id].category = "IMMEDIATE"
        return store[hypothesis_id]

    def _remember(
        self,
        character_id: str,
        *,
        event_id: str | None,
        observation_id: str | None,
        report_id: str | None = None,
        memory_type: str,
        salience: int,
        emotional_tags: list[str],
        persistence: int,
    ) -> MemoryRecord:
        memory = MemoryRecord(
            memory_id=self._id("memory"),
            character_id=character_id,
            event_id=event_id,
            observation_id=observation_id,
            report_id=report_id,
            memory_type=memory_type,
            salience=salience,
            emotional_tags=emotional_tags,
            created_at=self.world.clock.elapsed_seconds,
            last_recalled=self.world.clock.elapsed_seconds,
            persistence=persistence,
        )
        self.memories.setdefault(character_id, []).append(memory)
        self._emit(
            "MEMORY_FORMED",
            actor_id=character_id,
            payload={"memory_id": memory.memory_id, "memory_type": memory_type, "salience": salience},
        )
        return memory

    def _emit_belief_update(self, character_id: str, belief: BeliefRecord, reason: str) -> None:
        self._emit(
            "BELIEF_UPDATED",
            actor_id=character_id,
            payload={
                "hypothesis_id": belief.hypothesis_id,
                "confidence": belief.confidence,
                "certainty_class": belief.certainty_class.value,
                "reason": reason,
                "origin_groups_seen": len(belief.origin_groups_seen),
            },
        )

    def _emit(self, event_type: str, *, actor_id: str | None, payload: dict[str, Any], location_id: str | None = None, target_ids: tuple[str, ...] = ()) -> str:
        event = DomainEvent(
            event_id=self.world.entity_ids.next("event"),
            event_type=event_type,
            timestamp=self.world.clock.elapsed_seconds,
            actor_id=actor_id,
            target_ids=target_ids,
            location_id=location_id or "location-southern-grove",
            payload=payload,
            source="M3_INFORMATION",
            provenance=Provenance.GAME_EXTENSION.value,
        )
        self.event_bus.publish(event)
        self.event_bus.dispatch_pending()
        return event.event_id

    def _sync_world_state(self) -> None:
        self.simulation._sync_world_state()
        self.world.game_state["m3_information"] = self.to_dict()

    def _id(self, prefix: str) -> str:
        self._sequence += 1
        return self.world.entity_ids.next(prefix)

    def _peek_id(self, prefix: str) -> str:
        # Evidence relations need the id already assigned to their parent item.
        # The engine uses the last generated entity id deterministically.
        return self._last_entity_id(prefix)

    def _last_entity_id(self, prefix: str) -> str:
        return f"{prefix}-{self.world.entity_ids._next_number - 1:06d}"

    def _event(self, event_id: str) -> DomainEvent:
        for event in self.world.event_log:
            if event.event_id == event_id:
                return event
        raise InformationValidationError(f"unknown event: {event_id}")

    def _character(self, character_id: str):
        try:
            return self.simulation.characters[character_id]
        except KeyError as exc:
            raise InformationValidationError(f"unknown character: {character_id}") from exc

    @staticmethod
    def _source_key(evaluator_id: str, source_id: str) -> str:
        return f"{evaluator_id}::{source_id}"

    @staticmethod
    def _relationship_key(source_id: str, target_id: str) -> str:
        return f"{source_id}::{target_id}"

    def _root_report_id(self, report_id: str) -> str:
        seen: set[str] = set()
        current = report_id
        while current in self.reports and self.reports[current].parent_report_id and current not in seen:
            seen.add(current)
            current = self.reports[current].parent_report_id or current
        return current

    @staticmethod
    def _channel_delay(channel: Channel) -> int:
        return {
            Channel.FACE_TO_FACE: B["face_to_face_delay_seconds"],
            Channel.MARKET_GOSSIP: B["market_gossip_delay_seconds"],
            Channel.MESSENGER: B["messenger_delay_seconds"],
            Channel.LOCAL_NETWORK: B["local_network_delay_seconds"],
        }[channel]

    @staticmethod
    def _channel_quality(channel: Channel) -> int:
        return {
            Channel.FACE_TO_FACE: B["channel_quality_face_to_face"],
            Channel.MARKET_GOSSIP: B["channel_quality_market_gossip"],
            Channel.MESSENGER: B["channel_quality_messenger"],
            Channel.LOCAL_NETWORK: B["channel_quality_local_network"],
        }[channel]
