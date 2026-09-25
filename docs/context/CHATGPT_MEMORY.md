# ChatGPT Memory

## User goal

制作一个《蛊真人》世界观下的高开放度世界模拟 RPG。玩家是自创蛊师；原作人物、势力、蛊虫、杀招与历史作为世界组成部分存在。原作剧情不是强制主线，玩家和 NPC 的行为可以让局部世界线产生真实偏移。

## Stable product principles

- 小地图、完整规则闭环优先于大地图浅系统。
- Player 与 NPC 尽量遵守相同世界规则。
- Canon Database 与动态 World State 分离。
- 事实按 CANON_EXPLICIT / FAN_COMPILED / GAME_EXTENSION 分层。
- NPC 后续通过 Observation / Evidence / Report / Rumor / Belief 行动，不应无条件读取隐藏 WorldTruth。
- 核心成长不是通用 Character EXP，而是修为、空窍/真元、蛊虫资产、流派理解等独立轴。
- External ChatGPT 负责方向、Review 和 Gate；Codex 负责实现、测试、提交、Push 和交接。
- 用户偏好大任务包，但重大阶段仍人工 Gate。

## Vertical Slice direction

V0.1 目标是 10 个游戏日的局部世界切片，把修炼、蛊虫、经济、NPC、战斗、情报、势力和世界演化闭成循环。

## Review history

### M0 — PASS

Deterministic core established.

### M1 — PASS_WITH_NOTES

Reviewed remote HEAD:

`4d3523dc0fe42d799b34654e4ca2fe67ede6d82f`

M1 delivered a deterministic Day 1–2 living sandbox with:

- shared player/NPC Character;
- minimal cultivation;
- Gu hunger / feeding;
- finite resource node;
- finite local market;
- real inventory transfers;
- autonomous NPC actions;
- durable event log;
- save/resume equivalence;
- successful CI.

Non-blocking note: M1 NPC cadence is intentionally coarse and is not suitable for combat timing.

## Current state

Milestone: M2

Active task: TASK-M2-001

Goal: add the first deterministic hostile encounter with combat timing, perception/reaction, Gu use, movement, body-part injury, flee/attack risk and combat save/resume, without yet implementing the persistent M3 rumor/belief system or M7 killer-move graph.
