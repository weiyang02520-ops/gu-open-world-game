# 蛊真人开放世界同人游戏

这是一个“自创蛊师 + 动态世界规则”的高开放度世界模拟 RPG 原型。

核心目标不是按章节复刻原作剧情，而是建立一个会自行运行的蛊世界：玩家、NPC、蛊虫、资源、市场、势力和事件遵守统一规则，玩家行为能够真实改变局部世界状态与未来事件。

## 当前状态

- M0 deterministic core：**PASS**
- 当前里程碑：**M1**
- 当前任务：**TASK-M1-001 — Day 1~2 Headless Sandbox**
- 当前阶段仍以纯 Python Core Simulation 为主，不锁定最终图形引擎。

## 开发总方向

先做：

**小地图 + 完整系统闭环**

而不是：

**巨大五域地图 + 浅层功能**

V0.1 最终目标是一个 10 个游戏日的局部世界 Vertical Slice。

长期核心包括：

- 修炼 / 空窍 / 真元；
- GuDefinition / GuInstance / 喂养；
- 资源生态与真实市场库存；
- NPC Needs / Goals / Risk / Beliefs；
- 战斗与伤势；
- 情报 / 传闻 / 证据；
- 多维信誉与势力政治；
- 世界时间与分级模拟；
- Effect Graph 与杀招组合；
- Canon Database 与动态 World State 分离。

详细方向：

- `docs/PRODUCT_DIRECTION.md`
- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/CODEX_EXECUTION_POLICY.md`

## Codex 工作模式

项目默认使用“大任务模式”。

一个授权 Task 应尽量完成一个完整可验证闭环，包括代码、测试、smoke、文档、Memory、CI、Commit、Push 与 Remote Verify，而不是每完成几个文件就回来请求下一句话。

但仍然保留人工 Gate：

- Codex 不能自动跨 Milestone。
- 大方向和重要产品决策由用户 / External ChatGPT 决定。
- 每个阶段完成后进入 `WAITING_FOR_MASTER`。

## 本地运行

需要 Python 3.12+。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m gu_game --seed 42 --seconds 60
```

M1 完成后 README 应增加 Day 1~2 sandbox 的实际运行命令。

## 数据与设定

设定事实不得混为一谈。

- `CANON_EXPLICIT`：原作 / 明确作者来源
- `FAN_COMPILED`：书友 / Wiki / 社区整理
- `GAME_EXTENSION`：游戏为可玩性添加的规则与数值

不要把粉丝整理自动升级为 Canon。
不要在仓库中批量保存完整原著文本；保存结构化事实、摘要、来源定位与必要证据。

## 当前目录

```text
src/gu_game/       Python Core Simulation
data/canon/        原作明确设定
data/fan/          粉丝整理资料
data/game/         游戏扩展规则与平衡
tests/             自动测试
docs/              产品、架构、路线和 Memory
.ai/               当前任务 / 状态 / Review
.ai-handoff/       跨 Agent 阶段交接
```

GitHub remote：

`https://github.com/weiyang02520-ops/gu-open-world-game`
