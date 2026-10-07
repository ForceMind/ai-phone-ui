# 远端状态与历史边界

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

未部署 Pages/站点、未发布 release、未接入真实账号或模型。公开仓库和 DOM fixture 成功不能证明真实设备、持久存储 origin 或外部服务通过。
