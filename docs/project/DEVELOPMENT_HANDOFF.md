# 开发交接入口

## 产品与结构

以认可的 N9/Sailfish 融合 V3 为基线，展示名 SWIPE / AI。core 保留 V3 行为，suite 扩展页面，model 承载纯逻辑，workbench 只用于验收；screens.json 为 86 页唯一目录。

## 仓库与来源

公开仓库 [ForceMind/ai-phone-ui](https://github.com/ForceMind/ai-phone-ui) 在已有 LICENSE 提交后采用源码快照同步，不改写历史。原始五次提交、47b882b HEAD 与 v0.1.0-ui 注释标签保存在 bundle，未成为远端祖先或同名标签。根目录 LICENSE 保留；历史许可通知另存。

2026-10-06 工作区回退后，原始 ZIP、bundle 与源码可按哈希精确恢复；M0 文档/CI 编辑按已批准范围重建，再对实际重建树测试，不将丢失候选的报告当作本次证据。已上传的同 SHA 对象复用，新增内容重新校验。

## 接手步骤

```
git status --short
git branch --show-current
git log -6 --oneline
npm run build
npm run check
npm test
npm run test:ui
```

以实际远端 HEAD、PR 与 exact-head CI 为准。不要假设旧沙盒路径或旧报告代表当前成功。

## 不可遗漏

保留 Peek 反转、内容/边缘区别、子页 Pulley、固定快照确认、原片、草稿和无常驻底栏。退出/取消不是同意，服务预览不能写成已连接或已执行，前端不收集密钥。

查看 [当前状态](CURRENT_STATE.md)、[QA](../qa/TEST_REPORT.md) 和 [M2 下一步](NEXT_ACTION.md)。本批只关闭 M0 并登记有限既有工作卡；不扩大云服务范围。

## 2026-10-07 恢复后的本地提交

UI-011 已从记录重建并重新通过构建、25 静态/56 单元。浏览器启动受 socket 限制，0 断言；不称远端 CI 成功。原 M0 图集审批保持不变，远端仍只有 LICENSE。本地恢复分支及私有恢复包仅用于保存工作。详见 [恢复记录](RECOVERY_20261007.md) 与 [存储协议](../engineering/STORAGE_RECOVERY.md)。
