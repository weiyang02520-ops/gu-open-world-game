# 蛊真人开放世界同人游戏

这是一个“自创蛊师 + 动态世界规则”的高开放度世界模拟 RPG 原型。

## 当前状态

- M0 deterministic core：**PASS**
- M1 Day 1~2 Living Sandbox：**PASS_WITH_NOTES**
- M2 Combat / Injury / Reaction：**PASS_WITH_NOTES**
- 当前里程碑：**M3**
- 当前任务：**TASK-M3-001 — Information, Memory, Relationships and Rumor**

当前仍以纯 Python Core Simulation 为主。

## 已经跑通

```text
资源/市场/蛊食/修炼/NPC自主行为
+
整数毫秒战斗
→ 感知
→ Reaction Window
→ 闪避/命中
→ 部位伤势
→ 逃跑/脱战
→ Save/Resume确定性
```

## 当前 M3 要证明

```text
World Event
→ Observation
→ Evidence
→ Report
→ Rumor
→ Belief
→ Memory / Relationship
→ 不完整信息下的 NPC Decision
```

要求同一件真实事件能让不同 NPC 因为看到/听到的内容不同，形成不同甚至错误的判断，并采取不同动作。

详细要求见：

- `docs/M3_TASK_SPEC.md`
- `docs/PRODUCT_DIRECTION.md`
- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/CODEX_EXECUTION_POLICY.md`

## 工作模式

采用大任务模式：代码 → 测试 → smoke → 文档 → Memory → CI → Commit → Push → Remote Verify。

Codex 不自动跨 Milestone，每阶段结束进入 `WAITING_FOR_MASTER`。

## 现有 smoke

```powershell
python -m gu_game --scenario day1-2 --seed 20260925
python -m gu_game --scenario m2 --seed 20260925
python -m gu_game --scenario m3 --seed 20260925
```

M3 smoke 会运行直接观察、延迟谣言、结构化变异、不同 NPC 决策和最小调查。

M3 架构说明见 `docs/M3_ARCHITECTURE.md`。

GitHub remote:

`https://github.com/weiyang02520-ops/gu-open-world-game`
