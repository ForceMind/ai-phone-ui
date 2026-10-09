# 远端状态与历史边界

## 当前软件与在线交付（2026-10-09 UTC 核验）

- [PR21](https://github.com/ForceMind/ai-phone-ui/pull/21)、[PR22](https://github.com/ForceMind/ai-phone-ui/pull/22)、[PR23](https://github.com/ForceMind/ai-phone-ui/pull/23) 已正常合并。核对 main 为 [`cbd74ae9ab8fb874a3d92153418c6d7385d4065f`](https://github.com/ForceMind/ai-phone-ui/commit/cbd74ae9ab8fb874a3d92153418c6d7385d4065f)；PR22 的子页评论仍属未复现，PR23 只修复独立的原生结果正文对比缺陷。
- 该 main 的 [UI quality 37814165971](https://github.com/ForceMind/ai-phone-ui/actions/runs/37814165971) 两个 job 成功，含 26 静态、134 单元、既有桌面原生焦点 41、核心流程 10、D4 50、子页读位 8、结果正文 8。原方法、RED、artifact 与图像验收记录继续保留在 [PR23](https://github.com/ForceMind/ai-phone-ui/pull/23) 及 [正文对比报告](../qa/V4_NATIVE_RESULT_CONTRAST.md)。
- GitHub Pages 已通过既有 Actions 正式部署：[run 37929476325](https://github.com/ForceMind/ai-phone-ui/actions/runs/37929476325)，同一 source SHA，Configure Pages、Upload dist、Deploy 均成功。公开入口 [https://forcemind.github.io/ai-phone-ui/](https://forcemind.github.io/ai-phone-ui/) 只读复核 HTTP 200，正文 297625 字节，与该 main 的 `dist/index.html` 一致，SHA256 为 `5536221c36b79528d79f007d6c759a8533bb965279943755eaa17c6f7d843da2`。启用 Pages 没有更改 main 代码。
- 旧 [Pages run 37814166144](https://github.com/ForceMind/ai-phone-ui/actions/runs/37814166144) 的失败是保留的历史事实，不能覆盖上述后续成功，也不删除或改写该失败记录。

已交付的是离线 UI 工作台及其同字节在线展示。Android/iOS 实机、软键盘、系统字号、VoiceOver/TalkBack、设备内存/存储压力仍未验证；完整 D4/M2 不关闭，桌面回归与 HTTP/字节核验不替代这些门槛。真实短信、电话、账号、模型及云手机接入仍未完成，均是后续独立范围。以下 M0/UI-011 内容保留为来源与发布历史。

## 已完成发布（2026-10-07）

[ForceMind/ai-phone-ui](https://github.com/ForceMind/ai-phone-ui) 公开源码已发布：

1. 原 LICENSE 提交 e5c33cbadedebcc4fb8f4d09132045f907bd7af0 保留为祖先
2. M0 快照 [dab0df96](https://github.com/ForceMind/ai-phone-ui/commit/dab0df965aab58636c893161c6d4a6ef205a948d)，树 20f494d2b9a119ee5ec526cb0c9ecac5ef208388，163 个文件逐一核对
3. UI-011 [8544894e](https://github.com/ForceMind/ai-phone-ui/commit/8544894e9c32511c9e3a03a47fe96c19ceaf7918)，树 25a804a7de786f5bec3797e6a55f1731d7fc9a55，168 个文件逐一核对

两次 main 更新均非 force，并检查预期父提交。旧“仅 LICENSE / 图集审批待处理”的记载属于发布前历史，不再是当前阻塞。

## 来源未改写

根目录 LICENSE blob 始终为 0ad25db4bd1d86c452db3f9602ccdbe172438f52。provenance/project-history.bundle SHA256 为 76c662253478dbcf8946d3d40e8b4818a62fc48adbc11cffe46c83246f09e2f7，已从 GitHub 正常克隆后复核。

原始 HEAD 47b882b43b70750f250ff945aa2b7f0468bb0855 的 5 次提交及原注释标签保存在 bundle 中；不声称是远端祖先，不在远端重新创建同名标签。历史待定许可通知保留，不能宣称原始版本原本采用 AGPL。见 [恢复说明](../../provenance/README.md)。

## CI 与发布范围

M0 [运行](https://github.com/ForceMind/ai-phone-ui/actions/runs/37594652789) 与 UI-011 [运行](https://github.com/ForceMind/ai-phone-ui/actions/runs/37595281482) 均成功，日志及 artifact 对应各自 exact HEAD。当前分支后来有任何更新，都应再核对该提交自己的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/workflows/ui-check.yml)。

当时未部署 Pages/站点、未发布 release、未接入真实账号或模型；Pages 已在上述 2026-10-09 记录中完成部署，其余边界不因此改变。公开仓库和 DOM fixture 成功不能证明真实设备、持久存储 origin 或外部服务通过。
