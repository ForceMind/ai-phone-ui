# 当前状态 — v0.1.0

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

[Draft PR #10](https://github.com/ForceMind/ai-phone-ui/pull/10) 从 `3299ba0` 开始，首个测试提交在真实 HTTP-origin Chromium 记录 25 个直接焦点/返回失败和 7 个文件选择启动超时。初版修复 `8e08e6b` 的原 25 静态、82 单元、127 DOM 与 19 native 存储/图像检查通过，新增键盘检查 30/41；剩余的文件选择启动和测试重新打开 Pulley 路径继续诊断，不能宣称本卡全绿。独立审阅还要求覆盖嵌套确认退回的焦点。详见 [按 SHA 分层的证据](../qa/UI014_FOCUS_EVIDENCE.json)。
