# 蛊真人开放世界同人游戏

一个“自创蛊师 + 动态世界规则”的高开放度世界模拟 RPG 原型。

## 当前状态

已经完成内部 checkpoint：

- M0：确定性核心
- M1：资源 / 市场 / 蛊食 / 修炼 / NPC
- M2：战斗 / Reaction Window / 部位伤势
- M3：Observation / Evidence / Report / Rumor / Belief / Memory
- M4：势力 / 案件 / 多维 Reputation / Governance / Mission
- M5：资源生态 / 多市场 / Shipment / Caravan / Shortage
- M6：Rank1 修炼 / 突破 / Path Attainment / Insight
- M7：Effect Graph / 多 Gu Killer Move / Stability / Research

当前阶段：

**M8 — Day1–10 V0.1 Final Acceptance**

当前不是图形游戏客户端，仍然是可测试、可存档、可复现的 headless 世界模拟核心。

## V0.1 已整合的主循环

```text
资源与市场
→ Gu 喂养
→ 修炼
→ NPC 自主行动
→ 战斗 / 伤势
→ 观察 / 证据 / 谣言 / Belief
→ 势力案件 / 声望 / Standing / Mission
→ Shortage / Shipment / Caravan
→ Breakthrough / Attainment
→ Effect Graph / Killer Move
→ Day1–10 世界演化
```

## Final V0.1 CLI

第一版可玩层也提供根目录入口。裸运行会执行可复现的 30 天 headless
试玩；加 `--interactive` 可逐日输入行动：

```powershell
python main.py
python main.py --scenario play --interactive
```

可玩层 API、动态事件、NPC Tick 和 Save/Load 说明见
`docs/PLAYABLE_LAYER.md`。它通过 `event_system`、`event_resolver`、
`npc_sim` 和 `save_load` 接口工作，不替换 M1–M8 的规则模块。

合作路线：

```powershell
python -m gu_game --scenario v0.1 --seed 20260925 --strategy cooperative
```

对抗路线：

```powershell
python -m gu_game --scenario v0.1 --seed 20260925 --strategy adversarial
```

相同 seed 双路线比较：

```powershell
python -m gu_game --scenario v0.1-compare --seed 20260925
```

旧阶段 smoke 仍然保留：

```powershell
python -m gu_game --scenario day1-2 --seed 20260925
python -m gu_game --scenario m2 --seed 20260925
python -m gu_game --scenario m3 --seed 20260925
python -m gu_game --scenario m4 --seed 20260925
python -m gu_game --scenario m5 --seed 20260925
python -m gu_game --scenario m6 --seed 20260925
python -m gu_game --scenario m7 --seed 20260925
```

## 核心原则

- 玩家不是钦定主角。
- 世界不会等玩家。
- Player 与 NPC 尽量共享规则。
- Canon Database 与动态 World State 分离。
- NPC / 势力不能偷看隐藏 WorldTruth。
- 修炼不使用通用 Character EXP。
- 社会评价不是单一 Reputation 数值。
- 市场和 Shipment 使用真实有限库存。
- Canon 事件未来按前置条件触发，不强制还原剧情。
- LLM 可以负责语言表现，但不能替代 deterministic Rule Engine。

## 数据来源

- CANON_EXPLICIT：明确原作/作者依据
- FAN_COMPILED：社区整理
- GAME_EXTENSION：为游戏模拟补充的规则和内容

当前 V0.1 大量本地名称、NPC、Gu 和平衡数值是 GAME_EXTENSION placeholder。

不要批量提交完整原著正文。

## 关键文档

- `docs/PRODUCT_DIRECTION.md`
- `docs/V0_1_FULL_EXECUTION_SPEC.md`
- `docs/V0_1_ACCEPTANCE_MATRIX.md`
- `docs/V0_1_CONTENT_TARGETS.md`
- `docs/M8_ARCHITECTURE.md`
- `docs/EXECUTOR_POLICY.md`
- `docs/GATE_SHA_PROTOCOL.md`

## 执行器

仓库不绑定某个 coding agent。

可由：

- ChatGPT Web
- Sol
- Astre
- Codex

接力开发。

仓库状态是唯一真实上下文。

本机执行器主要保留给 GUI、硬件、驱动、真实性能、物理演示等网页端无法完成的任务。

GitHub：

`https://github.com/weiyang02520-ops/gu-open-world-game`
