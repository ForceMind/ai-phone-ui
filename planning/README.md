# D2 核心闭环候选 — 2026-10-08

用户已于 2026-10-08 确认继续采用首批浅色主方向并保留深色。D1视觉决定已通过；D1代码仍须独立复核和exact-main门槛。当前独立D2分支将照片/资料/执行相关24页加入原7页，合计31页候选；其余55页保持V3，待D3逐组迁移。

共享内容表面、来源/版本、正文、清单、比较和确认采用同一语义配色；全部原业务action、存储、候选、一性确认及原图逻辑保留。V3回退和主题切换不写业务资料。新增core_flows_test覆盖浅深每个新页、退出/回退、原文→本机整理→取消/实际下载、固定照片导出、导入候选取消接续、备份跨任务及本机执行确认。真实外部执行服务未连接，不能把本机预览闭环写成真实服务回执。

本地26静态/119单元通过；本机Chromium启动socket EPERM，native测试待本head CI，不冒称通过。独立D1复核提出系统覆盖层可能改变底层长确认阅读位置，需要最小native复现；未复现前不当成已确认缺陷。当前批次不部署、不绕过D4实机/读屏/软键盘门槛。

下一步：exact-head CI及实际截图，关闭任何新失败；完成独立审查、正常合并和exact-main复核，然后迁移剩余九组页面。Pages配置独立处理。

# 可执行工作计划

保留原有 24 项 backlog 与 M0–M5 里程碑，没有重新规划范围。六张线上 Epic 映射 15 个既有未完成条目，各条目只映射一次；已完成历史项继续留在 JSON 记录。没有创建 GitHub Milestones，remoteMilestonesCreated 仍为 false。

## 已核对的线上 Epic

- [EPIC: Testing — M2 实机、存储恢复与无障碍](https://github.com/ForceMind/ai-phone-ui/issues/1)：UI-010, UI-011, UI-014
- [EPIC: Interaction Foundation](https://github.com/ForceMind/ai-phone-ui/issues/2)：UI-012, UI-017
- [EPIC: Task Runtime](https://github.com/ForceMind/ai-phone-ui/issues/3)：UI-015, UI-020, UI-022
- [EPIC: Imaging](https://github.com/ForceMind/ai-phone-ui/issues/4)：UI-018, UI-019, UI-021
- [EPIC: Cloud Environment](https://github.com/ForceMind/ai-phone-ui/issues/5)：UI-023, UI-024
- [EPIC: UI Inventory](https://github.com/ForceMind/ai-phone-ui/issues/6)：UI-013, UI-016

M0 已完成源码/原始历史/CI 交付。UI-011 原子恢复代码已发布，但真实存储/设备验收仍开放；下一批优先 Testing 的 UI-010/011/014。其余 Epic 仅登记原范围，不表示后端已连接或费用/权限已经批准。
