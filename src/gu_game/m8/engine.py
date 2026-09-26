"""Integrated deterministic Day1-10 V0.1 world slice."""

from __future__ import annotations

from heapq import heappop, heappush
from pathlib import Path
from typing import Any

from ..m1.models import (
    ActionIntent,
    ActionType,
    Character,
    Controller,
    CultivationState,
    GuDefinition,
)
from ..m1.simulation import Simulation
from ..m2.models import CombatGuRole, CombatStatus
from ..m3.models import BasisType, Channel, ReportClaim, ReportIntention
from ..m4.models import (
    FactionCaseStatus,
    FactionProposalType,
    FactionStandingLevel,
    MembershipStatus,
    SocialIdentity,
)
from ..m5.engine import EconomyLogisticsEngine
from ..m5.models import ShipmentStatus
from ..m6.engine import CultivationAttainmentEngine
from ..m6.models import BreakthroughMode, InsightType
from ..m7.engine import EffectGraphEngine
from ..save import save_world
from .models import (
    CanonAnchor,
    CanonAnchorStatus,
    ImportantNpcProfile,
    LocationNode,
    RemoteActorState,
    SimulationLevel,
    StrategyProfile,
)


class IntegratedV01Engine:
    """One small world integrating M1-M7 into a ten-day causal slice."""

    SCHEMA_VERSION = 1
    TARGET_GU_DEFINITIONS = 36

    EXTRA_NPC_NAMES = (
        "陆槐",
        "赵砚",
        "白芷",
        "韩渡",
        "曲石",
        "苏苇",
        "严岭",
        "宁舟",
        "莫桑",
        "谢槿",
        "程火",
        "魏尘",
        "秦墨",
        "陶川",
        "罗灯",
    )

    NPC_ROLES = (
        "security_officer",
        "merchant_steward",
        "investigator",
        "gatherer",
        "healer",
        "hunter",
        "guard",
        "scholar",
        "caravan_leader",
        "herbalist",
        "miner",
        "information_broker",
        "independent_cultivator",
        "quartermaster",
        "ferryman",
        "scout",
        "artisan",
        "rival",
    )

    HOME_LOCATIONS = (
        "location-southern-grove",
        "location-southern-grove",
        "location-southern-grove",
        "location-spirit-grove",
        "location-apothecary",
        "location-beast-valley",
        "location-watchtower",
        "location-ash-study-hall",
        "location-caravan-rest",
        "location-herb-terrace",
        "location-old-mine",
        "location-river-crossing",
        "location-redleaf-forest",
        "location-river-crossing",
        "location-ferry",
        "location-cliff-trail",
        "location-ruined-kiln",
        "location-bandit-bend",
    )

    def __init__(self, effects: EffectGraphEngine) -> None:
        self.effects = effects
        self.cultivation = effects.cultivation
        self.economy = self.cultivation.economy
        self.information = self.cultivation.information
        self.factions = self.cultivation.factions
        self.combat = effects.combat
        self.simulation = effects.simulation
        self.world = effects.world

        self.locations: dict[str, LocationNode] = {}
        self.important_npcs: dict[str, ImportantNpcProfile] = {}
        self.remote_actors: dict[str, RemoteActorState] = {}
        self.anchors: dict[str, CanonAnchor] = {}
        self.completed_day: int = 0
        self.active_strategy: StrategyProfile | None = None
        self.flags: dict[str, Any] = {}
        self.day_history: list[dict[str, Any]] = []

        saved = self.world.game_state.get("m8_integrated")
        if saved:
            self._load_dict(saved)
        else:
            self._bootstrap_integrated_state()
        self._sync_world_state()

    @classmethod
    def new(cls, seed: int) -> "IntegratedV01Engine":
        simulation = Simulation.new(seed)
        cls._bootstrap_extra_characters(simulation)
        economy = EconomyLogisticsEngine.from_simulation(simulation)
        cls._expand_gu_catalog(simulation, economy)
        economy._sync_world_state()
        cultivation = CultivationAttainmentEngine.from_economy(economy)
        effects = EffectGraphEngine.from_cultivation(cultivation)
        return cls(effects)

    @classmethod
    def load(cls, path: str | Path) -> "IntegratedV01Engine":
        return cls(EffectGraphEngine.load(path))

    def save(self, path: str | Path) -> Path:
        self._sync_world_state()
        return save_world(self.world, path)

    @staticmethod
    def _bootstrap_extra_characters(simulation: Simulation) -> None:
        for index, name in enumerate(IntegratedV01Engine.EXTRA_NPC_NAMES):
            character_id = simulation.world.entity_ids.next("character")
            aptitude = 48 + (index * 3) % 31
            character = Character(
                character_id=character_id,
                name=name,
                controller=Controller.AI,
                location_id="location-southern-grove",
                currency=22 + index % 9,
                cultivation=CultivationState(
                    aptitude=aptitude,
                    aperture_capacity=92 + aptitude // 5,
                    primeval_current=52 + index % 12,
                    primeval_maximum=100,
                ),
            )
            simulation.characters[character_id] = character
            simulation.npc_ids.append(character_id)
        simulation._sync_world_state()

    @staticmethod
    def _expand_gu_catalog(
        simulation: Simulation, economy: EconomyLogisticsEngine
    ) -> None:
        names = (
            "Dewdrop Gu",
            "Reed Step Gu",
            "Ember Needle Gu",
            "Stone Ear Gu",
            "Moss Cloak Gu",
            "River Breath Gu",
            "Copper Shell Gu",
            "Mist Eye Gu",
            "Ash Thread Gu",
            "Bark Grip Gu",
            "Needle Wing Gu",
            "Silt Sense Gu",
            "Lantern Moth Gu",
            "Red Leaf Gu",
            "Quiet Foot Gu",
            "Pebble Skin Gu",
            "Spring Pulse Gu",
            "Herb Scent Gu",
            "Cliff Hook Gu",
            "Dust Veil Gu",
            "Hound Nose Gu",
            "Water Dart Gu",
            "Iron Jaw Gu",
            "Willow Bend Gu",
            "Cinder Spark Gu",
            "Echo Beetle Gu",
            "Mud Burrow Gu",
            "Pale Thread Gu",
            "Ferry Mark Gu",
            "Cold Dew Gu",
            "Stone Needle Gu",
            "Green Husk Gu",
            "Cloud Reed Gu",
            "Watchfire Gu",
            "Hollow Bell Gu",
            "Vine Knot Gu",
        )
        foods = list(economy.resource_groups["food"])
        needed = max(0, IntegratedV01Engine.TARGET_GU_DEFINITIONS - len(simulation.gu_definitions))
        created: list[str] = []
        for index in range(needed):
            definition_id = f"gu-v01-{index + 1:02d}"
            if definition_id in simulation.gu_definitions:
                created.append(definition_id)
                continue
            simulation.gu_definitions[definition_id] = GuDefinition(
                definition_id=definition_id,
                name=names[index % len(names)],
                rank=1,
                food_definition_id=foods[index % len(foods)],
                feed_quantity=1 + index % 3,
                hunger_per_hour=4 + index % 8,
                satiety_maximum=100,
                provenance="GAME_EXTENSION",
            )
            created.append(definition_id)

        if not created:
            created = [
                key for key in simulation.gu_definitions if key.startswith("gu-v01-")
            ]
        for index, npc_id in enumerate(simulation.npc_ids):
            while len(simulation.characters[npc_id].owned_gu_ids) < 3:
                gu_definition_id = created[
                    (index * 3 + len(simulation.characters[npc_id].owned_gu_ids))
                    % len(created)
                ]
                simulation._add_gu(npc_id, gu_definition_id, satiety=70)

    def _bootstrap_integrated_state(self) -> None:
        self._bootstrap_locations()
        self._bootstrap_npc_profiles()
        self._bind_resources_and_factions()
        self._bootstrap_anchors()
        self.refresh_lod()
        self._sync_world_state()

    def _bootstrap_locations(self) -> None:
        specs = (
            ("location-southern-grove", "Southern Grove", "MAIN_SETTLEMENT", "subregion-grove"),
            ("location-grove-market", "Grove Market", "MARKET_WARD", "location-southern-grove"),
            ("location-clan-compound", "Grove Compound", "FACTION_HQ", "location-southern-grove"),
            ("location-training-yard", "Training Yard", "TRAINING", "location-clan-compound"),
            ("location-apothecary", "Herbal Court", "HEALING", "location-southern-grove"),
            ("location-south-gate", "South Gate", "GATE", "location-southern-grove"),
            ("location-caravan-rest", "Caravan Rest", "ROUTE_STOP", "subregion-road"),
            ("location-river-crossing", "River Crossing", "SMALL_SETTLEMENT", "subregion-river"),
            ("location-river-dock", "River Dock", "MARKET_WARD", "location-river-crossing"),
            ("location-ferry", "Old Ferry", "TRAVEL", "location-river-crossing"),
            ("location-reed-bank", "Reed Bank", "RESOURCE_AREA", "subregion-river"),
            ("location-ash-camp", "Ash Camp", "SMALL_SETTLEMENT", "subregion-ash"),
            ("location-ash-market", "Ash Market", "MARKET_WARD", "location-ash-camp"),
            ("location-ash-study-hall", "Ash Study Hall", "FACTION_HQ", "location-ash-camp"),
            ("location-old-mine", "Old Mine", "RESOURCE_AREA", "subregion-ash"),
            ("location-hidden-ash-grotto", "Hidden Ash Grotto", "HIDDEN_INHERITANCE", "subregion-ash"),
            ("location-spirit-grove", "Spirit Grass Grove", "RESOURCE_AREA", "subregion-wilds"),
            ("location-redleaf-forest", "Redleaf Forest", "RESOURCE_AREA", "subregion-wilds"),
            ("location-beast-valley", "Beast Valley", "DANGER_AREA", "subregion-wilds"),
            ("location-mist-marsh", "Mist Marsh", "RESOURCE_AREA", "subregion-wilds"),
            ("location-stone-quarry", "Stone Quarry", "RESOURCE_AREA", "subregion-wilds"),
            ("location-old-shrine", "Old Shrine", "RUIN", "subregion-wilds"),
            ("location-cliff-trail", "Cliff Trail", "ROUTE", "subregion-road"),
            ("location-bandit-bend", "Bandit Bend", "DANGER_ROUTE", "subregion-road"),
            ("location-herb-terrace", "Herb Terrace", "RESOURCE_AREA", "subregion-wilds"),
            ("location-spring-cave", "Spring Cave", "RESOURCE_AREA", "subregion-wilds"),
            ("location-watchtower", "South Watchtower", "SECURITY", "subregion-road"),
            ("location-ruined-kiln", "Ruined Kiln", "RUIN", "subregion-ash"),
        )
        for location_id, name, kind, parent in specs:
            self.locations[location_id] = LocationNode(
                location_id, name, kind, parent, hidden="hidden" in location_id
            )

        edges = (
            ("location-southern-grove", "location-grove-market", 5),
            ("location-southern-grove", "location-clan-compound", 8),
            ("location-clan-compound", "location-training-yard", 4),
            ("location-southern-grove", "location-apothecary", 7),
            ("location-southern-grove", "location-south-gate", 10),
            ("location-south-gate", "location-caravan-rest", 30),
            ("location-caravan-rest", "location-river-crossing", 50),
            ("location-river-crossing", "location-river-dock", 5),
            ("location-river-crossing", "location-ferry", 6),
            ("location-river-crossing", "location-reed-bank", 15),
            ("location-river-crossing", "location-cliff-trail", 45),
            ("location-cliff-trail", "location-ash-camp", 50),
            ("location-ash-camp", "location-ash-market", 5),
            ("location-ash-camp", "location-ash-study-hall", 8),
            ("location-ash-camp", "location-old-mine", 30),
            ("location-old-mine", "location-hidden-ash-grotto", 35),
            ("location-ash-camp", "location-ruined-kiln", 20),
            ("location-southern-grove", "location-spirit-grove", 25),
            ("location-spirit-grove", "location-redleaf-forest", 35),
            ("location-redleaf-forest", "location-beast-valley", 45),
            ("location-redleaf-forest", "location-herb-terrace", 25),
            ("location-herb-terrace", "location-spring-cave", 30),
            ("location-beast-valley", "location-mist-marsh", 50),
            ("location-mist-marsh", "location-reed-bank", 40),
            ("location-spirit-grove", "location-stone-quarry", 40),
            ("location-stone-quarry", "location-old-shrine", 30),
            ("location-caravan-rest", "location-watchtower", 12),
            ("location-watchtower", "location-bandit-bend", 35),
            ("location-bandit-bend", "location-cliff-trail", 40),
        )
        for left, right, minutes in edges:
            self.locations[left].neighbors[right] = minutes
            self.locations[right].neighbors[left] = minutes

    def _bootstrap_npc_profiles(self) -> None:
        faction_cycle = (
            "faction-grove-watch",
            "faction-river-traders",
            "faction-ash-study",
            None,
        )
        for index, npc_id in enumerate(self.simulation.npc_ids[: len(self.NPC_ROLES)]):
            home = self.HOME_LOCATIONS[index]
            faction_id = faction_cycle[index % len(faction_cycle)]
            profile = ImportantNpcProfile(
                npc_id,
                self.NPC_ROLES[index],
                faction_id,
                home,
                [self.NPC_ROLES[index].upper(), "SURVIVE", "IMPROVE_POSITION"],
                60 + index % 31,
            )
            self.important_npcs[npc_id] = profile
            self.simulation.characters[npc_id].location_id = home
            self.remote_actors[npc_id] = RemoteActorState(
                npc_id,
                home,
                SimulationLevel.ABSTRACT,
                self.world.clock.elapsed_seconds,
            )

    def _bind_resources_and_factions(self) -> None:
        resource_locations = (
            "location-spirit-grove",
            "location-redleaf-forest",
            "location-beast-valley",
            "location-mist-marsh",
            "location-stone-quarry",
            "location-herb-terrace",
            "location-spring-cave",
            "location-old-mine",
            "location-reed-bank",
            "location-ruined-kiln",
        )
        for index, node_id in enumerate(sorted(self.economy.nodes)):
            self.simulation.resource_nodes[node_id].location_id = resource_locations[
                index % len(resource_locations)
            ]

        headquarters = {
            "faction-grove-watch": "location-southern-grove",
            "faction-river-traders": "location-river-crossing",
            "faction-ash-study": "location-ash-camp",
        }
        for faction_id, location_id in headquarters.items():
            if faction_id in self.factions.definitions:
                self.factions.definitions[faction_id].headquarters_location_id = location_id
            if faction_id in self.factions.states:
                self.factions.states[faction_id].controlled_locations = [location_id]

    def _bootstrap_anchors(self) -> None:
        npc_ids = self.simulation.npc_ids
        self.anchors["anchor-local-inspection"] = CanonAnchor(
            "anchor-local-inspection",
            [npc_ids[0]],
            "location-southern-grove",
            ["M5_SHORTAGE_DECLARED"],
            7,
            9,
            "DIVERGE_IF_PREREQUISITES_FAIL",
            "GAME_EXTENSION",
        )
        self.anchors["anchor-study-gathering"] = CanonAnchor(
            "anchor-study-gathering",
            [npc_ids[2]],
            "location-ash-study-hall",
            ["M6_INSIGHT_GAINED"],
            6,
            10,
            "SKIP_IF_PARTICIPANT_UNAVAILABLE",
            "GAME_EXTENSION",
        )
        self.anchors["anchor-caravan-arrival"] = CanonAnchor(
            "anchor-caravan-arrival",
            [npc_ids[8]],
            "location-river-crossing",
            ["M5_SHIPMENT_DEPARTED"],
            8,
            10,
            "OUTCOME_DEPENDS_ON_WORLD_STATE",
            "GAME_EXTENSION",
        )

    def refresh_lod(self) -> None:
        player_location = self.simulation.characters[self.simulation.player_id].location_id
        distances = self._hop_distances(player_location)
        for location_id, location in self.locations.items():
            hops = distances.get(location_id, 99)
            if hops == 0:
                level = SimulationLevel.ACTIVE
            elif hops == 1:
                level = SimulationLevel.NEAR
            elif hops <= 3:
                level = SimulationLevel.REGIONAL
            else:
                level = SimulationLevel.ABSTRACT
            if location.hidden and location_id != player_location:
                level = SimulationLevel.ABSTRACT
            location.level = level

        now = self.world.clock.elapsed_seconds
        for actor_id, state in self.remote_actors.items():
            character = self.simulation.characters[actor_id]
            state.location_id = character.location_id
            state.level = self.locations.get(
                state.location_id,
                LocationNode(state.location_id, state.location_id, "UNKNOWN", None),
            ).level
            if state.next_action_at <= 0:
                state.next_action_at = now + self._lod_interval(state.level)

    def travel(self, character_id: str, destination_id: str) -> int:
        if destination_id not in self.locations:
            raise ValueError("unknown destination")
        character = self.simulation.characters[character_id]
        minutes = self._shortest_travel_minutes(character.location_id, destination_id)
        if minutes is None:
            raise ValueError("destination is unreachable")
        origin = character.location_id
        self.advance_seconds(minutes * 60)
        character.location_id = destination_id
        self.simulation._emit(
            "M8_TRAVEL_COMPLETED",
            actor_id=character_id,
            location_id=destination_id,
            payload={
                "origin": origin,
                "destination": destination_id,
                "travel_minutes": minutes,
            },
        )
        if character_id == self.simulation.player_id:
            self.refresh_lod()
        self._sync_world_state()
        return minutes

    def advance_seconds(self, seconds: int) -> None:
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        if seconds == 0:
            return
        self.economy.advance_time(seconds, run_npcs=False)
        self.information.process_elapsed_time(seconds)
        self.factions.process_elapsed_time(seconds)
        self._process_remote_actors()
        self.evaluate_anchors()
        self._sync_world_state()

    def _process_remote_actors(self) -> None:
        self.refresh_lod()
        now = self.world.clock.elapsed_seconds
        for actor_id in sorted(self.remote_actors):
            state = self.remote_actors[actor_id]
            interval = self._lod_interval(state.level)
            if state.next_action_at <= 0:
                state.next_action_at = now + interval
            while state.next_action_at <= now:
                self._run_remote_action(actor_id, state)
                state.action_count += 1
                state.next_action_at += interval

    def _run_remote_action(self, actor_id: str, state: RemoteActorState) -> None:
        profile = self.important_npcs.get(actor_id)
        role = profile.role if profile else "worker"
        action = "IDLE"
        if role in {"gatherer", "hunter", "herbalist", "miner"}:
            node_ids = sorted(self.economy.nodes)
            node_id = node_ids[state.action_count % len(node_ids)]
            node = self.simulation.resource_nodes[node_id]
            if node.current_stock > 0:
                self.economy.gather(actor_id, node_id, 1)
                action = "GATHER"
        elif role in {"merchant_steward", "quartermaster", "caravan_leader", "ferryman"}:
            market_id = self.economy.MARKET_IDS[state.action_count % len(self.economy.MARKET_IDS)]
            self.economy.create_market_belief(actor_id, market_id)
            action = "OBSERVE_MARKET"
        elif role in {"security_officer", "guard", "scout", "investigator"}:
            route = self.economy.routes[sorted(self.economy.routes)[state.action_count % len(self.economy.routes)]]
            route.patrol_strength = min(100, route.patrol_strength + 1)
            action = "PATROL"
        elif role in {"scholar", "independent_cultivator"}:
            path_id = "path-wisdom" if role == "scholar" else "path-strength"
            self.cultivation.gain_insight(
                actor_id,
                path_id,
                insight_type=InsightType.OBSERVATION,
                source_key=f"remote-routine:{actor_id}:{state.action_count % 3}",
                base_value=1,
            )
            action = "STUDY"
        else:
            action = "LOCAL_WORK"

        self.economy.npc_goals[actor_id] = f"{role.upper()}_{action}"
        state.last_action = action
        self.simulation._emit(
            "M8_REMOTE_NPC_ACTION",
            actor_id=actor_id,
            location_id=state.location_id,
            payload={
                "role": role,
                "action": action,
                "simulation_level": state.level.value,
            },
        )

    def evaluate_anchors(self) -> None:
        event_types = {event.event_type for event in self.world.event_log}
        current_day = self.world.clock.elapsed_seconds // 86_400 + 1
        for anchor in self.anchors.values():
            if anchor.status is CanonAnchorStatus.RESOLVED:
                continue
            participants_available = all(
                participant in self.simulation.characters
                for participant in anchor.expected_participants
            )
            if current_day > anchor.latest_day:
                if anchor.status is not CanonAnchorStatus.RESOLVED:
                    anchor.status = CanonAnchorStatus.DIVERGED
                continue
            if current_day < anchor.earliest_day:
                anchor.status = CanonAnchorStatus.PENDING
                continue
            prerequisites_met = all(item in event_types for item in anchor.prerequisites)
            anchor.status = (
                CanonAnchorStatus.ELIGIBLE
                if participants_available and prerequisites_met
                else CanonAnchorStatus.PENDING
            )

    def resolve_anchor(self, anchor_id: str) -> CanonAnchor:
        anchor = self.anchors[anchor_id]
        if anchor.status is not CanonAnchorStatus.ELIGIBLE:
            raise ValueError("canon anchor is not currently eligible")
        anchor.status = CanonAnchorStatus.RESOLVED
        self.simulation._emit(
            "M8_CANON_ANCHOR_RESOLVED",
            actor_id=None,
            location_id=anchor.location_id,
            payload={
                "anchor_id": anchor_id,
                "provenance": anchor.provenance,
                "divergence_policy": anchor.divergence_policy,
            },
        )
        self._sync_world_state()
        return anchor

    def run_to_day(self, strategy: StrategyProfile | str, target_day: int = 10) -> dict[str, Any]:
        strategy = StrategyProfile(strategy)
        if target_day < self.completed_day or target_day > 10:
            raise ValueError("target_day must be between current progress and 10")
        if self.active_strategy is None:
            self.active_strategy = strategy
        elif self.active_strategy is not strategy:
            raise ValueError("a saved integrated run cannot switch strategy")

        while self.completed_day < target_day:
            day = self.completed_day + 1
            self._run_day(day, strategy)
            self._advance_to_day_end(day)
            self.completed_day = day
            snapshot = self.snapshot()
            self.day_history.append(
                {
                    "day": day,
                    "strategy": strategy.value,
                    "event_count": snapshot["event_count"],
                    "player_currency": snapshot["player"]["currency"],
                    "stage": snapshot["player"]["stage"],
                    "active_shortages": snapshot["economy"]["active_shortages"],
                }
            )
            self._sync_world_state()
        return self.snapshot()

    def _run_day(self, day: int, strategy: StrategyProfile) -> None:
        if day == 1:
            self._day1_survival(strategy)
        elif day == 2:
            self._day2_cultivation(strategy)
        elif day == 3:
            self._day3_resource_pressure(strategy)
        elif day == 4:
            self._day4_combat(strategy)
        elif day == 5:
            self._day5_information_and_faction(strategy)
        elif day == 6:
            self._day6_breakthrough(strategy)
        elif day == 7:
            self._day7_missions(strategy)
        elif day == 8:
            self._day8_shortage(strategy)
        elif day == 9:
            self._day9_killer_move(strategy)
        elif day == 10:
            self._day10_caravan_outcome(strategy)

        if strategy is StrategyProfile.COOPERATIVE:
            self._feed_player_core_gu()

    def _day1_survival(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        quantity = 8 if strategy is StrategyProfile.COOPERATIVE else 12
        self.economy.gather(player_id, self.simulation.RESOURCE_NODE_ID, quantity)
        if strategy is StrategyProfile.COOPERATIVE:
            if self.simulation.characters[player_id].inventory_quantity(self.simulation.FOOD_RESOURCE_ID) >= 2:
                self.economy.sell(
                    player_id,
                    self.economy.MARKET_IDS[0],
                    self.simulation.FOOD_RESOURCE_ID,
                    2,
                )
        else:
            self.economy.npc_goals[player_id] = "HOARD_RESOURCES"

    def _day2_cultivation(self, strategy: StrategyProfile) -> None:
        self.cultivation.cultivate(self.simulation.player_id, hours=4)

    def _day3_resource_pressure(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        node_id = "resource-node-m5-01"
        crisis_resource = self.simulation.resource_nodes[node_id].resource_definition_id
        river = self.economy.MARKET_IDS[1]
        self.flags["crisis_resource"] = crisis_resource
        self.economy.demand[river][crisis_resource] = 24
        if strategy is StrategyProfile.COOPERATIVE:
            self.economy.gather(player_id, node_id, 4)
            quantity = min(
                4, self.simulation.characters[player_id].inventory_quantity(crisis_resource)
            )
            if quantity:
                self.economy.sell(player_id, river, crisis_resource, quantity)
        else:
            self.economy.gather(player_id, node_id, 9)
            self._steal_from_market(player_id, river, crisis_resource, 3)
        self.economy.refresh_shortages(force=True)
        self.simulation._emit(
            "M8_RESOURCE_PRESSURE_VISIBLE",
            actor_id=None,
            location_id=self.simulation.markets[river].location_id,
            payload={
                "resource_id": crisis_resource,
                "strategy": strategy.value,
                "demand": self.economy.demand[river][crisis_resource],
            },
        )

    def _day4_combat(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        npc_id = self.simulation.npc_ids[0]
        if strategy is StrategyProfile.COOPERATIVE:
            attacker, defender = npc_id, player_id
        else:
            attacker, defender = player_id, npc_id
        self.simulation.characters[attacker].location_id = "location-southern-grove"
        self.simulation.characters[defender].location_id = "location-southern-grove"
        encounter = self.combat.start_encounter(
            (attacker, defender),
            positions={attacker: 0, defender: 4},
            location_id="location-southern-grove",
        )
        attack_profile = self.combat.profile_for_role(attacker, CombatGuRole.ATTACK)
        self.combat.declare_attack(
            encounter.encounter_id,
            attacker,
            defender,
            attack_profile.profile_id,
        )
        self.combat.advance_ticks(encounter.encounter_id, 4)
        if encounter.status is CombatStatus.ACTIVE:
            self.combat._end_encounter(
                encounter, CombatStatus.DISENGAGED, "m8_incident_ended", attacker
            )
        hit_event = next(
            event
            for event in reversed(self.world.event_log)
            if event.event_type == "ATTACK_HIT"
            and event.payload.get("encounter_id") == encounter.encounter_id
        )
        self.flags["combat_encounter_id"] = encounter.encounter_id
        self.flags["combat_hit_event_id"] = hit_event.event_id
        self.flags["combat_attacker_id"] = attacker
        self.flags["combat_defender_id"] = defender

    def _day5_information_and_faction(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        witness = self.simulation.npc_ids[2]
        receiver = self.simulation.npc_ids[1]
        opener = self.simulation.npc_ids[0]
        event_id = self.flags["combat_hit_event_id"]
        event = next(item for item in self.world.event_log if item.event_id == event_id)
        self.simulation.characters[witness].location_id = event.location_id or "location-southern-grove"
        self.simulation.characters[receiver].location_id = event.location_id or "location-southern-grove"

        hypothesis_id = f"hyp:m8:{strategy.value}:player-aggressor"
        hypothesis = self.information.register_hypothesis(
            hypothesis_id,
            player_id,
            "initiated_attack",
            True,
        )
        observation = self.information.observe_event(witness, event_id, distance=3)
        if observation is None:
            raise RuntimeError("M8 witness could not observe combat incident")
        supports = strategy is StrategyProfile.ADVERSARIAL
        evidence = self.information.create_evidence(
            witness,
            observation.observation_id,
            evidence_type="WITNESS_TESTIMONY",
            supports=[
                (
                    hypothesis.hypothesis_id,
                    60 if supports else 0,
                    0 if supports else 60,
                )
            ],
        )
        report = self.information.create_report(
            witness,
            receiver,
            [ReportClaim(hypothesis.hypothesis_id, True, supports, 90)],
            channel=Channel.FACE_TO_FACE,
            claimed_basis=BasisType.FIRST_HAND,
            actual_basis=BasisType.FIRST_HAND,
            asserted_confidence=90,
            evidence_references=[evidence.evidence_id],
            intention=ReportIntention.WARN,
        )
        self.information.advance_time(0)

        faction_id = "faction-grove-watch"
        self.factions.ingest_report(faction_id, receiver, report.report_id)
        identity = self.factions._identity_for_character(player_id)
        case = self.factions.open_case(
            faction_id,
            opener,
            identity.identity_id,
            [hypothesis.hypothesis_id],
            [report.report_id],
        )
        self.factions.investigate_case(case.case_id, receiver, event_id)
        self.flags["case_id"] = case.case_id
        self.flags["player_identity_id"] = identity.identity_id
        self.flags["hypothesis_id"] = hypothesis.hypothesis_id

        if strategy is StrategyProfile.COOPERATIVE:
            proposal = self.factions.create_proposal(
                faction_id,
                opener,
                FactionProposalType.CLOSE_CASE,
                target_identity_id=identity.identity_id,
                case_id=case.case_id,
                rationale=["INDEPENDENT_EVIDENCE", "PLAYER_NOT_AGGRESSOR"],
                cost=0,
                risks=0,
            )
            self.factions.evaluate_proposal(proposal.proposal_id)
            self.factions.recruit(faction_id, player_id, opener)
            river_sponsor = self._issuer_for("faction-river-traders", "RECRUIT")
            self.factions.recruit("faction-river-traders", player_id, river_sponsor)
            self.factions.set_reputation(
                faction_id, identity.identity_id, danger=20, trust=82, competence=68
            )
            self.factions.set_reputation(
                "faction-river-traders",
                identity.identity_id,
                danger=18,
                trust=80,
                competence=72,
            )
        else:
            for target_faction in ("faction-grove-watch", "faction-river-traders"):
                proposer = self._issuer_for(target_faction, "PROPOSE")
                proposal = self.factions.create_proposal(
                    target_faction,
                    proposer,
                    FactionProposalType.WATCH_SUBJECT,
                    target_identity_id=identity.identity_id,
                    case_id=case.case_id if target_faction == faction_id else None,
                    rationale=["VIOLENCE_RISK", "UNSTABLE_OUTSIDER"],
                    cost=0,
                    risks=0,
                )
                self.factions.evaluate_proposal(proposal.proposal_id)
            self.factions.set_reputation(
                faction_id, identity.identity_id, danger=88, trust=18, competence=70
            )
            self.factions.set_reputation(
                "faction-river-traders",
                identity.identity_id,
                danger=75,
                trust=22,
                competence=65,
            )

        self._apply_relationship_consequences(strategy)
        self._apply_goal_consequences(strategy)

    def _day6_breakthrough(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        if strategy is StrategyProfile.COOPERATIVE:
            self.cultivation.rest(player_id, hours=4)
            self.cultivation.cultivate(
                player_id, hours=6, method_id="method-deep-circulation"
            )
            if not self.cultivation.profiles[player_id].breakthrough_ready:
                self.cultivation.cultivate(player_id, hours=1)
            result = self.cultivation.attempt_breakthrough(
                player_id, BreakthroughMode.SAFE
            )
        else:
            self.cultivation.rest(player_id, hours=2)
            self.cultivation.cultivate(player_id, hours=5)
            result = self.cultivation.attempt_breakthrough(
                player_id, BreakthroughMode.FORCED
            )
        self.flags["breakthrough_result"] = result.to_dict()

    def _day7_missions(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        crisis_resource = self.flags["crisis_resource"]
        river = "faction-river-traders"
        issuer = self._issuer_for(river, "ISSUE_MISSION")
        mission = self.factions.generate_mission(
            river,
            issuer,
            "GATHER",
            target_id=crisis_resource,
            required_quantity=3,
        )
        self.flags["player_mission_id"] = mission.mission_id

        if strategy is StrategyProfile.COOPERATIVE:
            self.factions.accept_mission(mission.mission_id, player_id)
            node_id = "resource-node-m5-01"
            needed = max(
                0,
                3
                - self.simulation.characters[player_id].inventory_quantity(
                    crisis_resource
                ),
            )
            if needed:
                self.economy.gather(player_id, node_id, needed)
            self._deliver_supply_mission(mission.mission_id, player_id)
            ignored = self.factions.generate_mission(
                "faction-grove-watch",
                self._issuer_for("faction-grove-watch", "ISSUE_MISSION"),
                "WATCH_TARGET",
            )
            self.flags["ignored_mission_id"] = ignored.mission_id
        else:
            self.flags["ignored_mission_id"] = mission.mission_id

        npc_id = self.simulation.npc_ids[2]
        ash_mission = self.factions.generate_mission(
            "faction-ash-study",
            self._issuer_for("faction-ash-study", "ISSUE_MISSION"),
            "DELIVER_MESSAGE",
            target_id=player_id,
        )
        self.factions.accept_mission(ash_mission.mission_id, npc_id)
        message = self.information.create_report(
            npc_id,
            player_id,
            [],
            channel=Channel.FACE_TO_FACE,
            claimed_basis=BasisType.FIRST_HAND,
            actual_basis=BasisType.FIRST_HAND,
            asserted_confidence=70,
            intention=ReportIntention.INFORM,
        )
        self.information.advance_time(0)
        self.factions.progress_mission(ash_mission.mission_id, npc_id, 1)
        self.factions.complete_mission(ash_mission.mission_id, npc_id)
        self.flags["npc_mission_id"] = ash_mission.mission_id
        self.flags["npc_message_id"] = message.report_id

    def _day8_shortage(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        crisis_resource = self.flags["crisis_resource"]
        river = self.economy.MARKET_IDS[1]
        self.economy.demand[river][crisis_resource] += 8
        if strategy is StrategyProfile.COOPERATIVE:
            self.economy.gather(player_id, "resource-node-m5-01", 5)
            quantity = min(
                5,
                self.simulation.characters[player_id].inventory_quantity(
                    crisis_resource
                ),
            )
            if quantity:
                self.economy.sell(player_id, river, crisis_resource, quantity)
            self.economy.gather(player_id, "resource-node-m5-02", 2)
        else:
            self.economy.gather(player_id, "resource-node-m5-01", 10)
            self.economy.gather(player_id, "resource-node-m5-02", 8)
            self._steal_from_market(player_id, river, crisis_resource, 2)
            self.economy.add_route_pressure(
                "route-grove-river", criminal=5, shortage=8
            )
        self.economy.refresh_shortages(force=True)

    def _day9_killer_move(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        gu_ids = list(self.simulation.characters[player_id].owned_gu_ids)
        if strategy is StrategyProfile.COOPERATIVE:
            self.cultivation.gain_insight(
                player_id,
                "path-movement",
                insight_type=InsightType.EXPERIMENTATION,
                source_key="m8-cooperative-composite",
                base_value=90,
            )
            move = self.effects.design_killer_move(
                player_id,
                "Threefold River Step",
                gu_ids[:3],
                "path-movement",
            )
            self._ensure_research_material(2)
            self.effects.research_killer_move(move.instance_id)
            self.effects.research_killer_move(move.instance_id)
        else:
            move = self.effects.design_killer_move(
                player_id,
                "Rushed Ash Lunge",
                gu_ids[:2],
                "path-movement",
            )
        self.flags["killer_move_instance_id"] = move.instance_id

    def _day10_caravan_outcome(self, strategy: StrategyProfile) -> None:
        crisis_resource = self.flags["crisis_resource"]
        self._ensure_origin_market_stock(crisis_resource, 3)
        shipment = self.economy.procure_for_faction(
            "faction-river-traders",
            crisis_resource,
            3,
            route_id="route-grove-river",
            guards=5,
        )
        self.flags["final_shipment_id"] = shipment.shipment_id
        if strategy is StrategyProfile.COOPERATIVE:
            route = self.economy.routes[shipment.route_id]
            self.advance_seconds(route.travel_hours * 3_600)
            self._release_faction_reserve_to_market(shipment.shipment_id)
        else:
            self._rob_shipment(shipment.shipment_id, self.simulation.player_id)
        self.economy.refresh_shortages(force=True)

    def _feed_player_core_gu(self) -> None:
        player_id = self.simulation.player_id
        actor = self.simulation.characters[player_id]
        required = len(actor.owned_gu_ids[:3])
        current = actor.inventory_quantity(self.simulation.FOOD_RESOURCE_ID)
        if current < required:
            node = self.simulation.resource_nodes[self.simulation.RESOURCE_NODE_ID]
            quantity = min(required - current, node.current_stock)
            if quantity > 0:
                self.economy.gather(
                    player_id, self.simulation.RESOURCE_NODE_ID, quantity
                )
        for gu_id in actor.owned_gu_ids[:3]:
            definition = self.simulation.gu_definitions[
                self.simulation.gu_instances[gu_id].definition_id
            ]
            if actor.inventory_quantity(definition.food_definition_id) >= definition.feed_quantity:
                self.simulation.execute(
                    ActionIntent(ActionType.FEED_GU, player_id, gu_id=gu_id)
                )

    def _steal_from_market(
        self, actor_id: str, market_id: str, resource_id: str, quantity: int
    ) -> None:
        market = self.simulation.markets[market_id]
        available = market.inventory_quantity(resource_id)
        quantity = min(quantity, available)
        if quantity <= 0:
            return
        actor = self.simulation.characters[actor_id]
        moved = self.simulation._take_from_collection(
            market.inventory,
            resource_id,
            quantity,
            owner_id=actor_id,
            location_id=actor.location_id,
        )
        for lot in moved:
            actor.add_lot(lot)
        self.simulation._emit(
            "M8_MARKET_THEFT",
            actor_id=actor_id,
            location_id=market.location_id,
            target_ids=(market_id,),
            payload={
                "resource_id": resource_id,
                "quantity": quantity,
                "market_stock_after": market.inventory_quantity(resource_id),
            },
        )
        self.economy._update_market(market_id, resource_id)

    def _deliver_supply_mission(self, mission_id: str, character_id: str) -> None:
        mission = self.factions.missions[mission_id]
        resource_id = mission.target_id
        if resource_id is None:
            raise RuntimeError("supply mission lacks target resource")
        actor = self.simulation.characters[character_id]
        quantity = mission.required_quantity
        if actor.inventory_quantity(resource_id) < quantity:
            raise RuntimeError("mission delivery inventory is incomplete")
        faction_economy = self.economy.factions[mission.faction_id]
        moved = self.simulation._take_from_collection(
            actor.inventory,
            resource_id,
            quantity,
            owner_id=mission.faction_id,
            location_id=self.factions.definitions[
                mission.faction_id
            ].headquarters_location_id,
        )
        for lot in moved:
            faction_economy.warehouse[lot.lot_id] = lot
            faction_economy.reserves[resource_id] = (
                faction_economy.reserves.get(resource_id, 0) + lot.quantity
            )
        self.factions.progress_mission(mission_id, character_id, quantity)
        self.factions.complete_mission(mission_id, character_id)
        self.simulation._emit(
            "M8_SUPPLY_MISSION_DELIVERED",
            actor_id=character_id,
            location_id=actor.location_id,
            payload={
                "mission_id": mission_id,
                "resource_id": resource_id,
                "quantity": quantity,
            },
        )

    def _ensure_research_material(self, quantity: int) -> None:
        player_id = self.simulation.player_id
        resource_id = "resource-refine-01"
        actor = self.simulation.characters[player_id]
        missing = max(0, quantity - actor.inventory_quantity(resource_id))
        if not missing:
            return
        market_id = "market-ash-camp"
        available = self.simulation.markets[market_id].inventory_quantity(resource_id)
        if available >= missing:
            self.economy.buy(player_id, market_id, resource_id, missing)
            return
        node = next(
            (
                node_id
                for node_id, node in self.simulation.resource_nodes.items()
                if node.resource_definition_id == resource_id
                and node.current_stock >= missing
            ),
            None,
        )
        if node is None:
            raise RuntimeError("no real refinement material is available for research")
        self.economy.gather(player_id, node, missing)

    def _ensure_origin_market_stock(self, resource_id: str, quantity: int) -> None:
        market = self.simulation.markets[self.economy.MARKET_IDS[0]]
        missing = max(0, quantity - market.inventory_quantity(resource_id))
        if missing <= 0:
            return
        node_id = next(
            node_id
            for node_id, node in self.simulation.resource_nodes.items()
            if node.resource_definition_id == resource_id
            and node.current_stock >= missing
        )
        player_id = self.simulation.player_id
        self.economy.gather(player_id, node_id, missing)
        self.economy.sell(
            player_id, self.economy.MARKET_IDS[0], resource_id, missing
        )

    def _rob_shipment(self, shipment_id: str, actor_id: str) -> None:
        shipment = self.economy.shipments[shipment_id]
        if shipment.status is not ShipmentStatus.IN_TRANSIT:
            raise RuntimeError("only in-transit shipment can be robbed")
        actor = self.simulation.characters[actor_id]
        for lot in shipment.cargo:
            lot.owner_id = actor_id
            lot.location_id = actor.location_id
            actor.inventory[lot.lot_id] = lot
        shipment.status = ShipmentStatus.LOST
        shipment.resolved_at = self.world.clock.elapsed_seconds
        self.economy.caravans[shipment.caravan_id].status = ShipmentStatus.LOST
        self.economy.add_route_pressure(shipment.route_id, criminal=8, shortage=8)
        self.simulation._emit(
            "M8_SHIPMENT_ROBBED",
            actor_id=actor_id,
            target_ids=(shipment_id, shipment.caravan_id),
            location_id=actor.location_id,
            payload={
                "cargo_quantity": sum(lot.quantity for lot in shipment.cargo),
                "resource_ids": sorted({lot.definition_id for lot in shipment.cargo}),
            },
        )

    def _release_faction_reserve_to_market(self, shipment_id: str) -> None:
        shipment = self.economy.shipments[shipment_id]
        if shipment.status is not ShipmentStatus.ARRIVED:
            return
        faction_id = shipment.recipient_faction_id
        if faction_id is None:
            return
        faction = self.economy.factions[faction_id]
        market = self.simulation.markets[shipment.destination_market_id]
        released = 0
        for cargo in shipment.cargo:
            lot = faction.warehouse.pop(cargo.lot_id, None)
            if lot is None:
                continue
            lot.owner_id = market.market_id
            lot.location_id = market.location_id
            market.inventory[lot.lot_id] = lot
            faction.reserves[lot.definition_id] = max(
                0, faction.reserves.get(lot.definition_id, 0) - lot.quantity
            )
            released += lot.quantity
            self.economy._update_market(market.market_id, lot.definition_id)
        self.simulation._emit(
            "M8_FACTION_RESERVE_RELEASED",
            actor_id=faction_id,
            target_ids=(market.market_id,),
            location_id=market.location_id,
            payload={
                "shipment_id": shipment_id,
                "quantity": released,
            },
        )

    def _apply_relationship_consequences(self, strategy: StrategyProfile) -> None:
        player_id = self.simulation.player_id
        for npc_id in self.simulation.npc_ids[:3]:
            relation = self.information.relationship(npc_id, player_id)
            if strategy is StrategyProfile.COOPERATIVE:
                relation.trust = min(100, relation.trust + 18)
                relation.respect = min(100, relation.respect + 12)
                relation.resentment = max(0, relation.resentment - 5)
            else:
                relation.trust = max(0, relation.trust - 20)
                relation.fear = min(100, relation.fear + 24)
                relation.resentment = min(100, relation.resentment + 16)
            relation.last_updated = self.world.clock.elapsed_seconds
            self.simulation._emit(
                "RELATIONSHIP_CHANGED",
                actor_id=npc_id,
                target_ids=(player_id,),
                location_id=self.simulation.characters[npc_id].location_id,
                payload={
                    "trust": relation.trust,
                    "fear": relation.fear,
                    "respect": relation.respect,
                    "resentment": relation.resentment,
                    "reason": "m8_case_and_behavior_consequence",
                },
            )

    def _apply_goal_consequences(self, strategy: StrategyProfile) -> None:
        if strategy is StrategyProfile.COOPERATIVE:
            goals = ("COOPERATE_WITH_PLAYER", "SECURE_SUPPLY", "VERIFY_PLAYER_RELIABILITY")
        else:
            goals = ("WATCH_PLAYER", "GUARD_CARAVAN", "INVESTIGATE_PLAYER")
        for npc_id, goal in zip(self.simulation.npc_ids[:3], goals):
            self.economy.npc_goals[npc_id] = goal
            self.simulation._emit(
                "M8_NPC_GOAL_CHANGED",
                actor_id=npc_id,
                target_ids=(self.simulation.player_id,),
                location_id=self.simulation.characters[npc_id].location_id,
                payload={"goal": goal},
            )

    def _issuer_for(self, faction_id: str, capability: str) -> str:
        office = next(
            (
                office
                for office in self.factions.offices.values()
                if office.faction_id == faction_id
                and office.active
                and capability in office.authority
            ),
            None,
        )
        if office is None:
            raise RuntimeError(f"no {capability} office for {faction_id}")
        return office.character_id

    def _advance_to_day_end(self, day: int) -> None:
        target = day * 86_400
        remaining = target - self.world.clock.elapsed_seconds
        if remaining > 0:
            self.advance_seconds(remaining)

    def _lod_interval(self, level: SimulationLevel) -> int:
        return {
            SimulationLevel.ACTIVE: 3_600,
            SimulationLevel.NEAR: 2 * 3_600,
            SimulationLevel.REGIONAL: 6 * 3_600,
            SimulationLevel.ABSTRACT: 24 * 3_600,
        }[level]

    def _hop_distances(self, origin: str) -> dict[str, int]:
        if origin not in self.locations:
            return {}
        distances = {origin: 0}
        queue = [origin]
        while queue:
            current = queue.pop(0)
            for neighbor in self.locations[current].neighbors:
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def _shortest_travel_minutes(self, origin: str, destination: str) -> int | None:
        if origin == destination:
            return 0
        if origin not in self.locations or destination not in self.locations:
            return None
        heap: list[tuple[int, str]] = [(0, origin)]
        best = {origin: 0}
        while heap:
            cost, current = heappop(heap)
            if current == destination:
                return cost
            if cost != best[current]:
                continue
            for neighbor, minutes in self.locations[current].neighbors.items():
                new_cost = cost + minutes
                if new_cost < best.get(neighbor, 10**9):
                    best[neighbor] = new_cost
                    heappush(heap, (new_cost, neighbor))
        return None

    def snapshot(self) -> dict[str, Any]:
        player_id = self.simulation.player_id
        player = self.simulation.characters[player_id]
        identity = self.factions._identity_for_character(player_id)
        crisis_resource = self.flags.get("crisis_resource")
        encounter_id = self.flags.get("combat_encounter_id")
        encounter = self.combat.encounters.get(encounter_id) if encounter_id else None
        player_gu = [
            self.simulation.gu_instances[gu_id]
            for gu_id in player.owned_gu_ids
        ]
        relationship_summary = {
            npc_id: self.information.relationship(npc_id, player_id).to_dict()
            for npc_id in self.simulation.npc_ids[:3]
        }
        standings = {}
        memberships = {}
        access = {}
        for faction_id in self.factions.definitions:
            standing = self.factions.standings.get(
                self.factions._standing_key(faction_id, identity.identity_id)
            )
            standings[faction_id] = standing.level.value if standing else "UNKNOWN"
            membership = self.factions.memberships.get(
                self.factions._membership_key(player_id, faction_id)
            )
            memberships[faction_id] = (
                membership.status.value if membership else MembershipStatus.OUTSIDER.value
            )
            access[faction_id] = self.factions.can_access_faction_warehouse(
                faction_id, player_id
            )

        beliefs = {}
        hypothesis_id = self.flags.get("hypothesis_id")
        if hypothesis_id:
            for npc_id in self.simulation.npc_ids[:3]:
                belief = self.information.belief(npc_id, hypothesis_id)
                beliefs[npc_id] = belief.to_dict() if belief else None

        market_state = {}
        if crisis_resource:
            for market_id in self.economy.MARKET_IDS:
                market = self.simulation.markets[market_id]
                market_state[market_id] = {
                    "stock": market.inventory_quantity(crisis_resource),
                    "price": market.price_for(crisis_resource),
                }

        node_state = {
            node_id: {
                "stock": self.simulation.resource_nodes[node_id].current_stock,
                "health": self.economy.nodes[node_id].health,
            }
            for node_id in ("resource-node-m5-01", "resource-node-m5-02")
        }

        event_counts: dict[str, int] = {}
        for event in self.world.event_log:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

        return {
            "strategy": self.active_strategy.value if self.active_strategy else None,
            "completed_day": self.completed_day,
            "days_elapsed": self.world.clock.elapsed_seconds // 86_400,
            "event_count": len(self.world.event_log),
            "event_types": event_counts,
            "content": {
                "locations": len(self.locations),
                "important_npcs": len(self.important_npcs),
                "factions": len(self.factions.definitions),
                "gu_definitions": len(self.simulation.gu_definitions),
                "feeding_requirements": self.feeding_requirement_count(),
                "resource_nodes": len(self.economy.nodes),
                "markets": len(self.economy.MARKET_IDS),
                "routes": len(self.economy.routes),
            },
            "player": {
                "currency": player.currency,
                "stage": player.cultivation.minor_stage,
                "primeval_current": player.cultivation.primeval_current,
                "wall_progress": player.cultivation.wall_progress,
                "fatigue": self.cultivation.profiles[player_id].fatigue,
                "instability": self.cultivation.profiles[player_id].instability,
                "inventory_quantity": sum(lot.quantity for lot in player.inventory.values()),
                "gu": {
                    gu.instance_id: {
                        "definition_id": gu.definition_id,
                        "satiety": gu.satiety,
                        "condition": gu.condition,
                    }
                    for gu in player_gu
                },
            },
            "killer_moves": self.effects.summary(player_id)["killer_moves"],
            "relationships": relationship_summary,
            "npc_goals": {
                npc_id: self.economy.npc_goals.get(npc_id)
                for npc_id in self.simulation.npc_ids[:3]
            },
            "combat": {
                "encounter_id": encounter_id,
                "actors": (
                    {
                        actor_id: state.body.summary()
                        for actor_id, state in encounter.actors.items()
                    }
                    if encounter
                    else {}
                ),
            },
            "markets": market_state,
            "resource_nodes": node_state,
            "beliefs": beliefs,
            "cases": {
                case_id: case.status.value
                for case_id, case in self.factions.cases.items()
            },
            "standings": standings,
            "memberships": memberships,
            "access": access,
            "missions": {
                mission_id: {
                    "status": mission.status,
                    "assignee_id": mission.assignee_id,
                    "progress": mission.progress,
                    "objective_type": mission.objective_type,
                }
                for mission_id, mission in self.factions.missions.items()
            },
            "proposals": {
                proposal_id: {
                    "type": proposal.proposal_type.value,
                    "status": proposal.status,
                    "resolution": proposal.resolution,
                }
                for proposal_id, proposal in self.factions.proposals.items()
            },
            "shipments": {
                shipment_id: shipment.status.value
                for shipment_id, shipment in self.economy.shipments.items()
            },
            "anchors": {
                anchor_id: anchor.status.value
                for anchor_id, anchor in self.anchors.items()
            },
            "remote_actions": {
                actor_id: state.action_count
                for actor_id, state in self.remote_actors.items()
            },
        }

    def feeding_requirement_count(self) -> int:
        return len(
            {
                (
                    item.food_definition_id,
                    item.feed_quantity,
                    item.hunger_per_hour,
                )
                for item in self.simulation.gu_definitions.values()
            }
        )

    @staticmethod
    def divergence_report(
        cooperative: dict[str, Any], adversarial: dict[str, Any]
    ) -> dict[str, Any]:
        dimensions = {
            "wealth": cooperative["player"]["currency"]
            != adversarial["player"]["currency"],
            "cultivation": (
                cooperative["player"]["stage"],
                cooperative["player"]["instability"],
            )
            != (
                adversarial["player"]["stage"],
                adversarial["player"]["instability"],
            ),
            "gu_condition": cooperative["player"]["gu"] != adversarial["player"]["gu"],
            "killer_move": cooperative["killer_moves"] != adversarial["killer_moves"],
            "relationships": cooperative["relationships"] != adversarial["relationships"],
            "npc_goals": cooperative["npc_goals"] != adversarial["npc_goals"],
            "combat_injury": cooperative["combat"] != adversarial["combat"],
            "markets": cooperative["markets"] != adversarial["markets"],
            "resource_nodes": cooperative["resource_nodes"] != adversarial["resource_nodes"],
            "shipment": cooperative["shipments"] != adversarial["shipments"],
            "belief_chain": cooperative["beliefs"] != adversarial["beliefs"],
            "faction_case": cooperative["cases"] != adversarial["cases"],
            "standings": cooperative["standings"] != adversarial["standings"],
            "membership_or_access": (
                cooperative["memberships"],
                cooperative["missions"],
                cooperative["access"],
            )
            != (
                adversarial["memberships"],
                adversarial["missions"],
                adversarial["access"],
            ),
            "future_proposals": cooperative["proposals"] != adversarial["proposals"],
        }
        return {
            "dimensions": dimensions,
            "different_count": sum(dimensions.values()),
            "passes": sum(dimensions.values()) >= 13,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "locations": {
                key: value.to_dict() for key, value in sorted(self.locations.items())
            },
            "important_npcs": {
                key: value.to_dict()
                for key, value in sorted(self.important_npcs.items())
            },
            "remote_actors": {
                key: value.to_dict()
                for key, value in sorted(self.remote_actors.items())
            },
            "anchors": {
                key: value.to_dict() for key, value in sorted(self.anchors.items())
            },
            "completed_day": self.completed_day,
            "active_strategy": self.active_strategy.value if self.active_strategy else None,
            "flags": dict(self.flags),
            "day_history": list(self.day_history),
        }

    def _load_dict(self, data: dict[str, Any]) -> None:
        if int(data.get("schema_version", 0)) > self.SCHEMA_VERSION:
            raise ValueError("M8 save is newer than this engine")
        self.locations = {
            key: LocationNode.from_dict(value)
            for key, value in data.get("locations", {}).items()
        }
        self.important_npcs = {
            key: ImportantNpcProfile.from_dict(value)
            for key, value in data.get("important_npcs", {}).items()
        }
        self.remote_actors = {
            key: RemoteActorState.from_dict(value)
            for key, value in data.get("remote_actors", {}).items()
        }
        self.anchors = {
            key: CanonAnchor.from_dict(value)
            for key, value in data.get("anchors", {}).items()
        }
        self.completed_day = int(data.get("completed_day", 0))
        strategy = data.get("active_strategy")
        self.active_strategy = StrategyProfile(strategy) if strategy else None
        self.flags = dict(data.get("flags", {}))
        self.day_history = list(data.get("day_history", []))

    def _sync_world_state(self) -> None:
        self.effects._sync_world_state()
        self.world.game_state["m8_integrated"] = self.to_dict()
