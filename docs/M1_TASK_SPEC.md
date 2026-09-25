# M1 Task Spec：Day 1~2 Sandbox

## Goal

在 M0 通过外部审查后，实现一个可以运行 Day 1~2 的纯 Python Sandbox：玩家和 NPC 都能采集资源，市场库存会变化，蛊会产生真实喂养需求，玩家可以修炼，世界时间持续推进。

## In scope

- 统一 `Character` 模型的最小玩家/NPC字段
- 3 只基础蛊与饥饿状态
- 真元与空窍最小状态
- 一个资源点、一个 LocalMarket、3~5 个 NPC
- 最小 Needs/Goals 与可验证的 NPC 行动
- 买、卖、采集、喂蛊、修炼
- 事件日志和确定性测试

## Out of scope

完整战斗、势力政治、谣言传播、完整杀招、炼蛊、商队、Day 10 Vertical Slice 和复杂 UI。

## Gate

M1 完成后停在 `WAITING_FOR_MASTER`。没有外部审查结论，不自动进入 M2。
