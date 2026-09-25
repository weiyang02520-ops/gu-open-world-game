# 蛊真人开放世界同人游戏

这是一个“自创蛊师 + 动态世界规则”的高开放度世界模拟 RPG 原型。

## 当前状态

- M0 deterministic core：**PASS**
- M1 Day 1~2 Living Sandbox：**PASS_WITH_NOTES**
- M2 Combat / Injury / Reaction：**PASS_WITH_NOTES**
- M3 Information / Rumor / Belief：**PASS_WITH_NOTES**
- 当前里程碑：**M4**
- 当前任务：**TASK-M4-001 — Factions, Reputation, Cases and Institutional Politics**

当前仍以纯 Python Core Simulation 为主。

## 已经跑通

```text
资源 / 市场 / 蛊食 / 修炼
→ NPC 自主行动
→ 战斗 / Reaction Window / 部位伤势
→ Observation / Evidence / Report / Rumor
→ per-NPC Belief / Memory / Relationship
→ 不完整信息下的不同决策
```

## 当前 M4 要证明

```text
个人 Belief
→ 势力 Institutional Belief
→ Case / Proposal
→ 职位与派系意见分歧
→ Governance
→ 官方 Standing / Recruitment / Mission / Sanction
```

关键要求：

- 个人好恶 != 群体 Reputation
- 群体 Reputation != 势力 Institutional Belief
- Institutional Belief != 官方 FactionStanding
- 犯罪传闻 != 自动定罪
- 一个长老的意见 != 整个势力态度
- 任务是由势力需要生成的机会，不是强制主线

详细要求见：

- `docs/M4_TASK_SPEC.md`
- `docs/PRODUCT_DIRECTION.md`
- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/CODEX_EXECUTION_POLICY.md`

## 工作模式

采用大任务模式：

代码 → 测试 → smoke → 文档 → Memory → CI → Commit → Push → Remote Verify。

Codex 不自动跨 Milestone，每阶段结束进入 `WAITING_FOR_MASTER`。

## 已有 smoke

```powershell
python -m gu_game --scenario day1-2 --seed 20260925
python -m gu_game --scenario m2 --seed 20260925
python -m gu_game --scenario m3 --seed 20260925
```

M4 完成后应增加 faction/institutional smoke。

GitHub remote:

`https://github.com/weiyang02520-ops/gu-open-world-game`
