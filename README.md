# 蛊真人开放世界同人游戏

这是一个“自创蛊师 + 动态世界规则”的开放世界模拟 RPG。当前目录是独立项目，和上级工作区已有的“末日堡垒”以及 `shirone-vercel-staging` 无关。

## 当前阶段

当前只执行 `TASK-M0-001`：建立可持续开发、可测试、可恢复的 Core Simulation 骨架。M0 不实现完整 NPC、战斗、市场、UI 或五域地图；完成后停在 `WAITING_FOR_MASTER`，等待外部审查。

## 本地运行

需要 Python 3.12 或更高版本。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m gu_game --seed 42 --seconds 60
```

如果只想运行测试，也可以使用系统中已安装的 `pytest`，项目通过 `pyproject.toml` 将 `src` 加入测试路径。

## M0 核心边界

- `WorldClock` 只保存整数秒，不读取墙上时钟。
- `DeterministicRNG` 使用独立的 `random.Random`，并将内部状态写入存档。
- `DomainEvent` 是不可变事件信封；`EventBus` 明确区分发布、排队和消费。
- `WorldState` 是权威状态，可通过带版本号的 JSON 保存和恢复。
- `Claim` 强制保留 `CANON_EXPLICIT`、`FAN_COMPILED`、`GAME_EXTENSION` 之一；不把粉丝整理自动升级为原作事实。

## 目录

```text
src/gu_game/       Python Core Simulation
data/canon/        原作明确设定（当前为空）
data/fan/          粉丝整理资料（当前为空）
data/game/         游戏扩展数值（当前为空）
tests/             M0 单元测试
.ai/               机器可读协作状态
.ai-handoff/       阶段交接资料
docs/context/      项目 Memory
```

## 远端状态

当前独立仓库尚未配置 GitHub remote。完成本地 M0 后，需要提供目标远端或授权创建远端，才能完成文档要求的 Push 与 Remote Verify。
