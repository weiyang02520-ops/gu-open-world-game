# M0 Core Simulation 设计说明

## 目标

让下一次 Codex 或外部审查能够仅凭仓库文件恢复当前状态，并在没有图形引擎的情况下运行可重复的规则测试。

## 选择

### Python 标准库优先

M0 使用 dataclass、enum、`random.Random`、JSON 和 `pathlib`。当前没有引入 ORM、Web 框架或游戏引擎，避免把尚未验证的表现层选择写死。

### 事件信封与显式消费

`DomainEvent` 只负责描述发生了什么，不直接承担业务规则。`EventBus.publish()` 将事件写入待处理队列和历史；`dispatch_pending()` 才调用订阅者。后续 Reducer 可以在消费阶段改变状态，且事件历史可用于审计。

### 时间与随机数

世界时间是整数秒，种子和 RNG 内部状态均进入存档。这样可以测试“同 Seed + 同输入”的轨迹一致性，并为未来回放保留基础。

### 存档版本

JSON 根对象带 `schema_version`。加载较新的未知版本会拒绝，未来迁移逻辑可以在 `WorldState.from_dict()` 附近集中管理。

### Provenance

原作设定、粉丝汇编和游戏扩展是三个互斥枚举值。每个 Claim 还保留证据级别、来源、时间范围和置信度；这为后续 Canon 数据库提供最小可用边界。

## 暂不实现

NPC Utility AI、资源生态、LocalMarket、蛊虫喂养、炼蛊、战斗、情报传播、势力政治、地图渲染和多级时间调度均留到 M1 以后，避免用“骨架”冒充业务完成。
