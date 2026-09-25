# Active Task

## TASK-M0-001

建立可持续开发、可测试、可由下一次 Codex / ChatGPT 完整恢复的 V0.1 Core Simulation 仓库骨架。

### Scope

- 项目结构、Python Core、WorldClock、deterministic RNG、EventBus
- 最小 WorldState、JSON Save/Load、Entity IDs
- Canon provenance model
- pytest、CI、README、Memory、Handoff

### Out of scope

完整 NPC AI、战斗、市场、蛊系统、复杂 UI、五域、蛊仙、Day 10。

### Stop condition

本 Task 完成后，`CURRENT_STATE.status` 必须为 `WAITING_FOR_MASTER`，`next_actor` 必须为 `chatgpt`。
