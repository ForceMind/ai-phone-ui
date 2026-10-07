# 远端状态与历史边界

公开仓库 [ForceMind/ai-phone-ui](https://github.com/ForceMind/ai-phone-ui) 使用用户批准的源码快照同步。在所有者 LICENSE 初始提交 `e5c33cbadedebcc4fb8f4d09132045f907bd7af0` 后新增普通提交，不覆盖历史、不 force push。

原始五次提交与 v0.1.0-ui 注释标签完整保存在 原始历史包，未成为 GitHub 祖先或远端标签。原始 HEAD 为 `47b882b43b70750f250ff945aa2b7f0468bb0855`，156 个跟踪文件可独立恢复。本快照仅叠加 M0 文档、CI、远端状态和许可元数据修正；UI 行为与 V3 原版不变。

根目录 LICENSE blob 保持 `0ad25db4bd1d86c452db3f9602ccdbe172438f52`；历史占位通知另存。现有连接可完成同步，无需新的 CLI 登录、凭据或持久授权。

## CI 证据

必须查看 [UI quality](https://github.com/ForceMind/ai-phone-ui/actions/workflows/ui-check.yml) 与当前提交 SHA 一致的运行。此快照的远端 CI 待核对，不能提前宣称通过。CI 先移除归档结果，记录 source-head.txt 并保留当次日志与产物；本地成功或历史 126/126 不能冒充远端成功。

2026-10-06 重建候选的本地 build/static/unit 单独复验。此前受限环境的浏览器在启动时失败，0 项断言；归档浏览器 126/126 仅为旧 DOM fixture 结果。即使 GitHub CI 通过，也不能替代 Android/iOS 实机、真实 origin 存储和相机/语音权限验收。

## 发布边界

仓库公开不等于网站部署；本批不启用 Pages、不部署、不发布 release、不接入真实服务。历史建仓脚本不用于此现有仓库。后续以实际远端、CI 和 [下一步](../project/NEXT_ACTION.md) 为准。
