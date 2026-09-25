# ChatGPT Memory

## Project goal

高开放度《蛊真人》世界模拟 RPG：玩家自创蛊师，NPC/市场/战斗/情报/势力遵守统一世界规则，原作剧情不是强制主线。

## Review history

- M0: PASS
- M1: PASS_WITH_NOTES
- M2: PASS_WITH_NOTES
- M3: CHANGES_REQUESTED

Reviewed M3 Gate:

`d13f7e71e5a7fa597c5d54efcc25d385eca54c09`

## M3 review finding

M3 has the required information-system skeleton and passes 28 tests/CI, but several semantic issues must be repaired before M4:

- relationship trust direction;
- inactive source-profile credibility fields;
- rumor mutation not affecting interpreted belief;
- impossible self-referential Gate SHA rule.

## Current state

Active task: TASK-M3-FIX-001

M4 is not authorized until this repair passes.
