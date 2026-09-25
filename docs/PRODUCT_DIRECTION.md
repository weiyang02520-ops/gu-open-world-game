# Product Direction — 《蛊真人》开放世界模拟 RPG

> Status: CURRENT
> Scope: V0.1 and long-term architecture
> Purpose: prevent implementation drift when ChatGPT / Codex / future agents continue the project.

## 1. Product thesis

This project is not a conventional quest RPG wearing a Gu-themed skin.

The intended product is:

**a living Gu-world simulation + freeform Gu Master RPG + Gu / killer-move construction + dynamic social/economic world**

The player creates an original Gu Master and enters a world that continues to move without waiting for the player.

Original characters, factions, locations, Gu, killer moves and historical events may appear as part of the world, but the original plot is not a mandatory player main quest.

The desired player feeling is:

> “I entered a world that already has its own rules and ambitions. I am not the chosen protagonist. I survive, cultivate, trade, deceive, fight, research and gradually force the world to notice me.”

## 2. Non-negotiable design principles

### 2.1 High openness is core, not decoration

The player must be able to solve the same pressure through multiple systemic routes.

Example: a Gu requires food.

Possible answers should include, when the surrounding systems support them:

- buy it;
- gather it;
- refine / substitute it;
- trade favors;
- borrow;
- steal;
- rob;
- manipulate information;
- join a faction to gain supply;
- move to another region;
- abandon / replace the Gu.

Do not replace this with a single quest marker.

### 2.2 The world continues when the player is absent

NPCs cultivate, trade, consume resources, travel, form goals and change local conditions.

A resource node does not wait for the player.
A market does not freeze when the player leaves.
An NPC does not remain in place forever because no quest is active.

### 2.3 Player and NPCs share world rules

Avoid “player-only magic”.

Player and NPCs should use the same core concepts:

- Character;
- cultivation / aperture / primeval essence;
- Gu ownership;
- inventory;
- actions;
- economic resources;
- injuries;
- information;
- faction membership;
- goals.

The primary difference is controller:

- HUMAN
- AI

### 2.4 Canon Database and World State are different systems

Canon Database answers:

> “What is the original setting / source claim?”

World State answers:

> “What is true in this save right now?”

Never overwrite source truth because a save diverged.

### 2.5 Original plot is a baseline timeline, not a railroad

Future canonical events should eventually be represented as event templates / timeline anchors with preconditions.

Before a canonical event can fire, the simulation should be able to ask:

- are key participants alive?
- do they still hold the necessary Gu / resources?
- is the location still controlled by the expected faction?
- do they still have the relevant goal?
- did required precursor events happen?

If not, the event may diverge instead of forcing the original scene.

### 2.6 Rules decide legality; language models do not invent physics

LLMs may later help with:

- natural-language dialogue;
- naming generated killer moves;
- summaries;
- NPC explanation;
- narration;
- semantic retrieval.

LLMs must not be allowed to directly declare an impossible world rule valid.

Rules / validators remain deterministic.

### 2.7 Small world, deep systems before huge world

V0.1 deliberately uses a small South Border local region.

Do not build Five Regions and Two Heavens before the local simulation is fun and explainable.

## 3. Player growth model

Do not use a generic Character Level as the core progression.

Growth should be composed of separate axes:

- cultivation rank and minor stage;
- aperture state;
- primeval essence amount / quality;
- aptitude;
- owned Gu;
- feeding and maintenance capacity;
- recipes / knowledge;
- killer moves;
- path attainment;
- relationships;
- reputation;
- faction status;
- wealth and resource access.

The intent is that two characters at the same cultivation rank can be radically different.

## 4. Gu design

Gu are not merely hotbar skills.

Long-term architecture must support:

- GuDefinition vs GuInstance;
- feeding;
- ownership / refinement;
- activation requirements;
- primeval essence cost;
- state / damage;
- effect composition.

Future Gu behavior should be expressible through an Effect Graph or equivalent compositional effect system.

Killer moves should ultimately be combinations of:

- core Gu;
- auxiliary Gu;
- activation ordering;
- resource flow;
- path compatibility;
- complexity;
- stability;
- attainment.

Do not implement every combination as a manually hard-coded skill.

## 5. NPC direction

NPCs should move toward:

**Needs + Goals + Knowledge/Beliefs + Relationships + Risk Evaluation + Utility / Planning**

Long-term NPC rule:

NPCs may act on wrong information.

They must not automatically read hidden WorldTruth.

Future information chain:

World Event
→ Observation
→ Evidence
→ Report
→ Rumor
→ Belief
→ Decision

This enables misinformation, concealment, investigation and misjudgment.

## 6. Social / faction direction

A faction is an actor with:

- resources;
- needs;
- institutional knowledge;
- goals;
- offices;
- members;
- internal political interests;
- external relations.

Do not reduce a faction to one reputation integer.

Keep separate:

- one NPC’s opinion of the player;
- public reputation among an audience;
- faction institutional belief;
- official faction standing.

## 7. Economy direction

Resources are real state.

Long-term rules:

- finite market inventory;
- finite resource nodes;
- regeneration / depletion;
- real transport;
- Gu feeding consumption;
- refinement material consumption;
- NPC demand;
- faction reserves;
- local market pricing.

Avoid infinite shops and unexplained respawn loops as the core economy.

## 8. Combat direction

Target direction:

**real-time simulation + pause + reaction windows**

Combat should eventually model:

- preparation;
- activation;
- detection;
- reaction;
- movement;
- defense;
- interruption;
- effect resolution;
- injuries;
- resource costs;
- aftermath.

Do not make combat only “HP - X”.

## 9. Time and simulation level

One authoritative WorldClock.

Different simulation precision is allowed:

- active / combat;
- near;
- regional;
- abstract.

A large future world is feasible only if remote simulation is aggregated.

## 10. Data provenance

Every lore fact must support provenance.

Primary categories:

- CANON_EXPLICIT
- FAN_COMPILED
- GAME_EXTENSION

Evidence level may include:

- EXPLICIT
- DERIVED
- INFERRED
- DISPUTED
- UNKNOWN

Do not ingest large copyrighted source text into the repository.
Store structured facts, summaries, source locations and minimal evidence needed for verification.

## 11. V0.1 product definition

V0.1 is a **10-game-day local-world vertical slice**.

By Day 10, different player strategies should create materially different states in:

- cultivation;
- wealth;
- Gu ownership / condition;
- NPC goals;
- NPC survival;
- relationships;
- market supply;
- prices;
- resource nodes;
- rumors;
- investigations / cases;
- faction standing;
- local security;
- shipment outcomes.

The event log must explain how those differences happened.

## 12. What V0.1 is not

V0.1 is not:

- full Five Regions;
- Gu Immortal endgame;
- complete canon database;
- graphical open-world rendering;
- a recreation of the novel chapter by chapter;
- a dialogue-only AI sandbox;
- a static quest game.

## 13. Presentation layer

Do not lock the final client engine yet.

Core simulation remains headless until enough of the 10-day vertical slice works.

When the simulation is stable enough, choose the presentation layer based on:

- iteration speed;
- UI / map needs;
- real-time combat needs;
- modability;
- save/debug tooling;
- deployment target.

Engine choice must not force a rewrite of domain rules.

## 14. Success signal

The project is on the correct path when a player can tell a story like:

> “I needed Gu food, the market was short, I stole it, someone saw me, a rumor spread, one NPC tried to blackmail me, I killed him, the local faction investigated, traders changed behavior, I lost access to the market, so I moved into a riskier resource route and developed differently.”

That story should emerge from interacting systems, not from a scripted branch tree.
