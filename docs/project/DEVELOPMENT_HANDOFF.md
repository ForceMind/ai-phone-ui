# 开发交接入口

## 先恢复事实

读取 AGENTS、CURRENT_STATE 与 NEXT_ACTION；先检查工作区、实际远端 HEAD 和该 SHA 的 CI。源码基线 [dab0df96](https://github.com/ForceMind/ai-phone-ui/commit/dab0df965aab58636c893161c6d4a6ef205a948d) 和 UI-011 [8544894e](https://github.com/ForceMind/ai-phone-ui/commit/8544894e9c32511c9e3a03a47fe96c19ceaf7918) 已发布，不要再从“仓库只有 LICENSE”或“待恢复上传认证”继续。

## 当前实现

保留 V3 的三视图、Peek、活动封面、Pulley、固定快照确认、原片、草稿和单 HTML；86 页目录仍为唯一来源。UI-011 由 storage.cjs 在恢复时一次提交 core/suite，失败保持旧资料和可重试确认；不靠双写回滚假装原子性。

UI-011 对应 CI 为 25 静态、56 单元、127 浏览器回归通过。测试 harness 仍是 DOM 注入/内存 storage；真实 origin、实机和并发标签冲突合并未证明。无外部服务连接或网站部署。

## 历史与接续

原 5 次提交/注释标签在 provenance 的原始 bundle 中，不在远端祖先图；根目录 LICENSE 原字节保留。先前工作区回退的恢复记载是历史，当前仓库可直接正常克隆。禁止 force push 或重建原始标签。

继续工作前运行 npm run build、npm run check、npm test、npm run test:ui；受限环境失败必须记录，不用旧报告替代。下一批仅按 [M2 卡](NEXT_ACTION.md) 验收真实存储/设备，UI-011 整项仍不应提前关闭。
