# 开发交接入口

## 先恢复事实

读取 AGENTS、CURRENT_STATE 与 NEXT_ACTION；先检查工作区、实际远端 HEAD 和该 SHA 的 CI。源码基线 [dab0df96](https://github.com/ForceMind/ai-phone-ui/commit/dab0df965aab58636c893161c6d4a6ef205a948d) 和 UI-011 [8544894e](https://github.com/ForceMind/ai-phone-ui/commit/8544894e9c32511c9e3a03a47fe96c19ceaf7918) 已发布，不要再从“仓库只有 LICENSE”或“待恢复上传认证”继续。

## 当前实现

保留 V3 的三视图、Peek、活动封面、Pulley、固定快照确认、原片、草稿和单 HTML；86 页目录仍为唯一来源。UI-011 由 storage.cjs 在恢复时一次提交 core/suite，失败保持旧资料和可重试确认；不靠双写回滚假装原子性。

UI-011 原 CI 为 25 静态、56 单元、127 DOM fixture。[PR #7](https://github.com/ForceMind/ai-phone-ui/pull/7) 的测试提交 `e82370e342fabc83eacd1ca322b40a5b576a10f4` 另通过 14/14 HTTP-origin 原生存储回归，已核对实际 artifact。没有变更运行时 JS。旧 fixture 仍完整保留，真实 origin suite 单独启动 loopback server、导入文件、点击确认并观察生产 reload。当前 head 仍须复核自身 CI，不能用测试提交证据替代。实机、大图/OS 压力和并发标签冲突合并未证明。无外部服务连接或网站部署。

## 历史与接续

原 5 次提交/注释标签在 provenance 的原始 bundle 中，不在远端祖先图；根目录 LICENSE 原字节保留。先前工作区回退的恢复记载是历史，当前仓库可直接正常克隆。禁止 force push 或重建原始标签。

继续工作前运行 npm run build、npm run check、npm test、npm run test:ui、npm run test:storage；受限环境失败必须记录，不用旧报告替代。下一批仅按 [M2 卡](NEXT_ACTION.md) 验收现有确认页键盘焦点；设备验证仍开放，UI-011 整项仍不应提前关闭。

## 本批跟踪文字边界

PR #7 进入既定审阅/合并流程，代码与 main 合并结果需分别核对 exact-head CI。Testing Epic #1 的进度正文更新被取消，已保持原样；这只是未更新的跟踪文字，不阻塞已授权的独立代码 PR 收尾，也不应另写评论或重试该 issue 修改。

合并后测试时序记录：713e44b 的首次 main CI 暴露 native harness 提前导航（12/14），详见 QA 报告。测试须等待 core ready 与 Workbench 初始 deep link 都就绪；只等 core 标志会被延迟旧路由覆盖。保留失败证据，不能以 PR 通过代替 main 通过。

## 本批图像边界接续

PR #9 已保存 test-only 失败证据，再加入确认前的真实图片验证，保持原 URL 字节、16MP 启动限制及单快照提交协议。普通照片导入的 1400px 工作副本没有改动。单元的 Image mock 仅覆盖 14 个入口分支，不替代新增 5 个 native 图片场景。必须核对 [图像证据](../qa/UI011_IMAGE_EVIDENCE.json) 的对应 SHA，并在收尾时查最终 head 与 main 自身 CI。不要重新创建图像范围或将 UI-011 整项关闭；下一张卡仍位于 M2。


## UI-014 当前有界接续

PR #10 只收敛现有照片导入/导出与备份确认的键盘进入、取消和任务接续，保持明确接受路径及 UI-011 原片/16MP/原子恢复回归。先记录真实浏览器 RED，再修复焦点与原任务返回；文件选择启动超时和测试脚本点错恢复后菜单要与产品缺陷区分。见 UI014_FOCUS_EVIDENCE.json；最终 head 与 main 都必须各自核对 artifact。完整 UI-014 仍不关闭，读屏、大字及实际手机尚未验证。

独立代码阅读另提示：确认页可保留在任务会话中，而 pendingFile / pendingRestore 候选是全局变量，可能存在跨确认候选隔离缺口。该项尚未由原生浏览器复现；单独下一张有界卡调查，不把焦点修复当作已解决候选绑定，也不修改已取消更新的 Epic #1。
