# Agent Memory

## 执行真相

- 独立项目目录：`gu-open-world-game`
- 当前 Task：`TASK-M0-001`
- 当前里程碑：M0
- M0 只实现纯 Python Core Simulation 骨架
- 完成后必须等待外部审查，不进入 M1

## 技术约束

- Python 3.12+
- 标准库优先；pytest 只作为开发测试依赖
- 时间和随机数必须可复现
- Save/Load 使用带 schema 版本的 JSON
- 不在 Core 中读取墙上时钟或全局随机状态

## 常见失败模式

- 把 `WorldState` 和表现层耦合
- 把 mock 或单元测试写成真实环境验证
- 把 FAN_COMPILED 当作 CANON_EXPLICIT
- 在 M0 预先实现完整业务系统
- 没有远端时声称 Push 或 Remote Verify 成功
