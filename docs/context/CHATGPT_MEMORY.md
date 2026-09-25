# ChatGPT Memory

## User goal

制作一个《蛊真人》世界观下的高开放度世界模拟 RPG。玩家是自创蛊师；原作人物、势力、蛊虫、杀招与历史作为世界组成部分存在。原作剧情不是强制主线，玩家和 NPC 的行为可以让局部世界线产生真实偏移。

## Stable product principles

- 小地图、完整规则闭环优先于大地图浅系统。
- Player 与 NPC 尽量遵守相同世界规则。
- Canon Database 与动态 World State 分离。
- 事实按 CANON_EXPLICIT / FAN_COMPILED / GAME_EXTENSION 分层。
- NPC 不应读取未来的全知 WorldTruth；后续通过 Observation / Evidence / Report / Rumor / Belief 行动。
- 核心成长不是通用 Character EXP，而是修为、空窍/真元、蛊虫资产、流派理解等独立轴。
- GitHub 是 ChatGPT Web 与 Codex 的长期协作真实状态源。
- External ChatGPT 负责架构、Review 和 Gate；Codex 负责实现、测试、提交、Push 和交接。
- 每个 Milestone 必须通过 Review Gate，禁止自动跨阶段。

## Vertical Slice direction

最终 V0.1 目标是 10 个游戏日的局部世界切片，依次把修炼、蛊虫、经济、NPC、战斗、情报、势力和世界演化闭成循环。

## Review history

### M0 — PASS

Reviewed remote commit:

`ba27a449af05484a437f46a650b1692fb1d121b2`

Verified:
- deterministic clock/RNG;
- RNG Save/Load continuation;
- versioned JSON world state;
- EventBus queue/history separation;
- Canon/Fan/Game provenance;
- pytest and GitHub Actions;
- correct stop at WAITING_FOR_MASTER.

M0 non-blocking hardening notes were carried into M1.

## Current state

Milestone: M1

Active task: TASK-M1-001

Goal: build the deterministic Day 1~2 headless sandbox with player/NPC shared Character state, minimal cultivation, three Gu instances with feeding, finite resource/market inventory and minimal autonomous NPC actions.
