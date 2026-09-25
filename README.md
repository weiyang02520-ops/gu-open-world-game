# 蛊真人开放世界同人游戏

这是一个“自创蛊师 + 动态世界规则”的高开放度世界模拟 RPG 原型。

核心目标不是按章节复刻原作剧情，而是建立一个会自行运行的蛊世界：玩家、NPC、蛊虫、资源、市场、势力和事件遵守统一规则，玩家行为能够真实改变局部世界状态与未来事件。

## 当前状态

- M0 deterministic core：**PASS**
- M1 Day 1~2 Living Sandbox：**PASS_WITH_NOTES**
- 当前里程碑：**M2**
- 当前任务：**TASK-M2-001 — Combat, Injury and Hostile Decision Loop**
- 当前仍以纯 Python Core Simulation 为主，不锁定最终图形引擎。

## 已经跑通

M1 已证明：

```text
有限资源点
→ 玩家 / NPC 采集
→ 真实 ResourceLot
→ 有限市场交易
→ 蛊虫饥饿 / 喂养
→ 修炼消耗真元和时间
→ NPC 自主行动
→ 世界时间推进
→ Save / Resume 可复现
```

## 当前 M2 要证明

```text
敌对意图
→ 蛊虫准备 / 激活
→ 感知
→ Reaction Window
→ 移动 / 闪避 / 逃跑
→ 攻击结算
→ 具体部位伤势
→ 后续行动受伤势影响
```

详细要求：

- `docs/M2_TASK_SPEC.md`
- `docs/PRODUCT_DIRECTION.md`
- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/CODEX_EXECUTION_POLICY.md`

## Codex 工作模式

采用“大任务模式”。

一个授权 Milestone 尽量一次完成完整可验证闭环：

代码 → 测试 → smoke → 文档 → Memory → CI → Commit → Push → Remote Verify。

但保留人工 Gate：

- Codex 不能自动跨 Milestone。
- 大方向由用户 / External ChatGPT 决定。
- 每个阶段完成后进入 `WAITING_FOR_MASTER`。

## 本地运行

需要 Python 3.12+。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m gu_game --seed 42 --seconds 60
.\.venv\Scripts\python.exe -m gu_game --scenario day1-2 --seed 20260925
```

M2 完成后 README 应增加 combat smoke 命令。

## 数据与设定

- `CANON_EXPLICIT`：原作 / 明确作者来源
- `FAN_COMPILED`：书友 / Wiki / 社区整理
- `GAME_EXTENSION`：游戏为可玩性添加的规则与数值

不要把粉丝整理自动升级为 Canon。
不要在仓库中批量保存完整原著文本。

GitHub remote：

`https://github.com/weiyang02520-ops/gu-open-world-game`
