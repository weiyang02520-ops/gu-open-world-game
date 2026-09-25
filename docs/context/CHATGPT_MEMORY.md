# ChatGPT Memory

## User goal

制作一个《蛊真人》世界观下的高开放度世界模拟 RPG。玩家是自创蛊师；世界应当自行运转，原作剧情不是强制主线。

## Stable principles

- 小地图 + 深系统闭环优先。
- Player 与 NPC 尽量共享规则。
- Canon Database 与动态 World State 分离。
- CANON_EXPLICIT / FAN_COMPILED / GAME_EXTENSION 分层。
- NPC 不应无条件读取隐藏 WorldTruth。
- 大任务包开发，但重大 Milestone 人工 Gate。
- External ChatGPT 负责方向/Review；Codex 负责实现/测试/Push。

## Review history

- M0: PASS
- M1: PASS_WITH_NOTES
- M2: PASS_WITH_NOTES

M2 reviewed remote HEAD:

`60b4b776ef18c5992ceb6b7ed3131feac7f17469`

M2 已跑通整数毫秒战斗、Reaction Window、具体部位伤势、真元消耗、逃跑和战斗 Save/Resume。

## Current state

Milestone: M3

Active task: TASK-M3-001

目标：让世界从“所有 NPC 都能看见真相”变成“NPC 只能基于观察、证据、转述、谣言和记忆形成自己的 Belief”，并让错误/不完整信息真正改变 NPC 行为。
