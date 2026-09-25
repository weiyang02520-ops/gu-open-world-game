# 蛊真人开放世界同人游戏

一个“自创蛊师 + 动态世界规则”的高开放度世界模拟 RPG 原型。

## 当前状态

已完成并通过 Review：

- M0：确定性核心
- M1：Day1–2 资源 / 市场 / 蛊食 / 修炼 / NPC
- M2：战斗 / Reaction Window / 部位伤势
- M3：Observation / Evidence / Report / Rumor / Belief / Memory / Relationship

当前唯一任务：

**TASK-V0.1-FULL-001 — 剩余 V0.1 一次性完成**

用户已授权 **M4→M8 连续执行**，内部阶段只做 checkpoint，不再等待人工 Gate。

## 一次跑完的剩余内容

```text
M4 势力 / 声望 / 案件 / 内部政治
↓
M5 资源危机 / 物流 / Shipment / Caravan / 市场扩展
↓
M6 Rank1完整修炼 / 突破 / Path Attainment
↓
M7 Effect Graph / 多蛊杀招组合 / 稳定度 / 研究
↓
M8 Day1–10完整纵切 / LOD / 双策略世界分歧
```

## 最终 V0.1 目标

- 10 个游戏日；
- 20–40 个重要地点目标；
- 15–30 个重要 NPC 目标；
- 3–5 个势力；
- 30–50 个 GuDefinition 目标；
- 至少 20 条有实际资源需求的喂养链；
- 15–25 个资源点；
- 3–4 个市场；
- 5–8 条路线；
- 实体 Shipment / Caravan；
- 案件 / 谣言 / Institutional Belief / 官方 Standing；
- Rank1 Initial→Middle→Upper→Peak；
- 安全 / 强行突破；
- Path Attainment / Insight；
- Effect Graph；
- 至少一个真正由多个 Gu 组成的杀招；
- 同 seed 的合作路线与对抗路线产生明显不同世界状态；
- Event Log 能解释为什么世界走成这样。

## Sol / Codex 必读

1. `docs/V0_1_FULL_EXECUTION_SPEC.md`
2. `docs/V0_1_ACCEPTANCE_MATRIX.md`
3. `docs/V0_1_CONTENT_TARGETS.md`
4. `docs/M4_TASK_SPEC.md`
5. `docs/PRODUCT_DIRECTION.md`
6. `docs/DEVELOPMENT_ROADMAP.md`
7. `docs/CODEX_EXECUTION_POLICY.md`
8. `docs/GATE_SHA_PROTOCOL.md`
9. `docs/context/AGENT_MEMORY.md`

## 工作模式

内部每阶段：

```text
实现
→ 测试
→ 全部旧回归
→ smoke
→ diff 自审
→ 文档 / Memory
→ commit
→ push
→ 继续下一阶段
```

**M4 / M5 / M6 / M7 完成后不要 WAITING_FOR_MASTER。**

只有完整 V0.1 完成后：

```text
status = WAITING_FOR_MASTER
next_actor = chatgpt
STOP
```

## 暂不做

- 图形客户端 / Unity / Godot 最终选型；
- 五域完整世界；
- 蛊仙；
- 福地 / 天劫；
- 宝黄天；
- 完整原作剧情复刻；
- 大规模原著正文导入；
- LLM 权威判定游戏规则。

GitHub:

`https://github.com/weiyang02520-ops/gu-open-world-game`
