# 当前状态 — v0.1.0

## 最新有界批次：长消息确认阅读

上一张候选隔离卡 PR #11 已正常合并为 main `2139d5e9a800b53dec890e1373c772eeeacc0432`，main run 37635186925 已核对 25/92/127/19/41/8 及 artifact。以下更早批次保留为历史记录。

[PR #12](https://github.com/ForceMind/ai-phone-ui/pull/12) 的 test-only `3491e207` 在真实 HTTP-origin Chromium 复现普通/大字长文不可滚读、无空格文本横向溢出以及键盘/纵向阅读失效；六条行为路径失败，异常/外部请求检查通过。首候选 `56d411b` 因继承文字选择使旧横滑取消回归失败（39/41），保留失败证据并只恢复原确认页的不可选择文字样式。

修正候选 `f16a9129aae5d4aeb483e2d67053cd33703ff5d9` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37639719218) 通过 25 静态、92 单元、127 DOM、19 native 存储/图像、41 native 键盘、8 native 候选及 8 native 阅读检查；ZIP、source-head 与三份构建文件字节已核对。普通/大字/不换行文本末尾、边界说明及跨任务阅读位置均有实际截图与几何证据。独立审阅无阻塞问题；最终像素收尾恢复原短确认标题颜色。见 [阅读证据](../qa/UI014_READING_EVIDENCE.json)。

这只是上述候选的通过结果。最终文档/样式 head 与正常合并 main 仍须分别核对 exact-head CI、artifact 和截图，不能沿用候选绿灯。完整 UI-014 仍开放，实际 Android/iOS、读屏、手机软键盘与 OS 字号未测；未调用真实消息/电话或外部服务。

## 已发布

2026-10-07 源码基线 [dab0df96](https://github.com/ForceMind/ai-phone-ui/commit/dab0df965aab58636c893161c6d4a6ef205a948d) 与独立 UI-011 修复 [8544894e](https://github.com/ForceMind/ai-phone-ui/commit/8544894e9c32511c9e3a03a47fe96c19ceaf7918) 已进入 main，并逐文件核对。保留原 LICENSE 初始提交和 LICENSE 字节，没有 force push。

86 个登记界面仍为 55 本机交互页、31 未连接服务预览页；保留 V3 三视图、Peek、活动封面、Pulley、原片和单 HTML。原始 5 次提交与 v0.1.0-ui 注释标签保存在 [不可变历史包](../../provenance/README.md)，未导入 GitHub 祖先图或重建远端标签。

## 已核对质量

- M0 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37594652789)：24/24 静态、32/32 单元、126/126 新浏览器回归
- UI-011 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37595281482)：25/25 静态、56/56 单元、127/127 新浏览器回归
- 已通过正常 Git clone 回读，历史包 SHA256 和 LICENSE blob 均匹配

这是对应上述提交的真实 Actions 结果。后续文档或代码提交仍应核对自身 SHA 的 CI；不能把旧报告直接当作最新成功。详见 [发布证据](../qa/PUBLICATION_EVIDENCE.json) 与 [测试报告](../qa/TEST_REPORT.md)。

## M2 / UI-011 真实存储证据

[PR #7](https://github.com/ForceMind/ai-phone-ui/pull/7) 的测试提交 `e82370e342fabc83eacd1ca322b40a5b576a10f4` 已由 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37598633407) 通过：25 静态、56 单元、原 127 DOM fixture，以及新增 14/14 真实 HTTP-origin 回归。真实文件输入、明确确认、原生 localStorage、整页 reload 和有界原生配额取消/重试均已执行；artifact 的 SHA256 和 source-head 已核对。没有修改产品运行时 JS。详见 [分层证据](../qa/UI011_ORIGIN_EVIDENCE.json)。本条对应明确提交，后续文档提交与合并后的 main 仍核对自身 SHA；最新合并状态以 PR 记录为准。

## M2 / UI-011 合成图恢复边界

[PR #9](https://github.com/ForceMind/ai-phone-ui/pull/9) 测试先行得到 17/19 native 结果：准确 16MP 和图像占用下配额流程通过；过大/不能解码的备份仍可进入旧确认。对应修复只在确认前验证图片加载、像素上限和解码，保留原片及原有持久化协议；新增 14 个入口单元处理边界与过时异步结果。[图像证据](../qa/UI011_IMAGE_EVIDENCE.json) 按 source SHA 区分失败、修复和最终核对，不以历史结果冒充新 HEAD。

## 尚未完成

UI-011 原子恢复代码已实现并通过自动化；HTTP-origin Chromium 的原生存储/配额回归已获得上述独立证据；实际设备大图内存、OS 磁盘压力、Android/iOS、系统边缘、软键盘和无障碍仍属于 M2。原 127 项 DOM fixture 与新增 14 项真实 origin 分开报告，均不代表实机结果。

模型、云手机、消息、电话、音乐、地图、OAuth、账单及日历账号均未连接；没有部署网站，也不是完整 Android 系统。存储本地且未加密，中心裁切/圆形选区不是语义抠图。下一张工作卡见 [NEXT_ACTION](NEXT_ACTION.md)。

## 计划映射

已从既有 backlog 建立六张 [Epic](../../planning/README.md)，覆盖 15 个未完成条目且无重复；没有扩大功能范围，也未创建远端 Milestones。


## M2 / UI-014 确认焦点与取消接续

[PR #10](https://github.com/ForceMind/ai-phone-ui/pull/10) 从 `3299ba0` 开始，首个测试提交在真实 HTTP-origin Chromium 记录 25 个直接焦点/返回失败和 7 个文件选择启动超时。修复候选 `a3da63073cd399745117be456ef57293795a6c95` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37608195038) 已通过 25 静态、84 单元、127 DOM、19 native 存储/图像与 41/41 native 键盘检查；artifact 摘要、source-head、构建 HTML 字节和截图均已核对。历史失败、harness 修正与通过证据分开记录，见 [按 SHA 分层的证据](../qa/UI014_FOCUS_EVIDENCE.json)。

这不是所有后续 head 或 main 的绿灯证明；最终小改（包括将恢复按钮的旧「确认导出」文案纠正为「确认恢复」）与合并 main 各自仍需 exact-head CI/artifact。完整 UI-014 仍开放，读屏、大字与实际手机未验证。


## M2 / 现有确认候选隔离

PR #10 已正常合并至 main df55643；该 main 的 run 37609773189 已由合并门槛核对 25/84/127/19/41。下一张有界卡是 [PR #11](https://github.com/ForceMind/ai-phone-ui/pull/11)：测试先行 d3430714 真正复现较新导入覆盖旧确认的候选，见 [按 SHA 分层证据](../qa/UI011_CANDIDATE_EVIDENCE.json)。修复只使照片/备份候选随确认共享并一次消费，不更改存储协议或页面。UI-011 与完整 UI-014 仍开放；本卡最终 head、正常合并 main 及 artifact 仍分别按门槛核对。

候选 `28975e3` 的 run 37611856799 已核对通过 25/92/127/19/41/8；artifact ZIP、source-head 与预览 HTML 匹配。独立 review 无阻塞问题；最终小改仅撤去可选文件名显示、同步文档与登记验收，仍须自己的 CI，再核对正常合并 main。
