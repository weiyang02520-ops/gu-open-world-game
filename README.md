# 蛊真人开放世界同人游戏

这是一个“自创蛊师 + 动态世界规则”的高开放度世界模拟 RPG 原型。

## 当前状态

- M0 deterministic core：**PASS**
- M1 Day 1~2 Living Sandbox：**PASS_WITH_NOTES**
- M2 Combat / Injury / Reaction：**PASS_WITH_NOTES**
- M3 Information / Rumor / Belief：**PASS_WITH_NOTES**
- 当前里程碑：**M4**
- 当前任务：**TASK-M4-001 — Factions, Reputation, Cases and Institutional Politics**
- M4：**实现完成，等待 External ChatGPT Review**

## M4 已跑通

```text
M3 Information
→ Institutional Belief
→ Faction Case / Proposal
→ Bloc / Office disagreement
→ Governance
→ Official Standing / Recruitment / Mission
```

## Smoke

```powershell
python -m gu_game --scenario day1-2 --seed 20260925
python -m gu_game --scenario m2 --seed 20260925
python -m gu_game --scenario m3 --seed 20260925
python -m gu_game --scenario m4 --seed 20260925
```

M4 架构说明见 `docs/M4_ARCHITECTURE.md`。

当前用户任务在 M4 Gate 停止，不开始 M5。

GitHub remote:

`https://github.com/weiyang02520-ops/gu-open-world-game`
