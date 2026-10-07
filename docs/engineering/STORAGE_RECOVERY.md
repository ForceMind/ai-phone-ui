# UI-011：恢复一致性

恢复原本先替换内存、分别写 core/suite、吞掉失败后仍 reload，会留下新旧混合资料。本修复是已审核工作在工作区回退后的重建，没有增加新功能。

## 协议

- 旧安装在首次成功恢复前继续使用原有两个 key，不在启动时迁移
- 已校验的恢复资料先复制、暂停任务和专注，再序列化为一个 `ai-phone-ui-state-v1` 快照
- 单次写入成功后才更新内存、消耗确认并 reload；失败保留旧资料和可重试确认，不 reload
- 后续普通保存更新同一个快照中的一部分，并保留另一部分
- 原有 key 只在提交成功后尽力清理；中断清理不改变新快照的权威性；无效快照不会回退拼接旧资料

采用 [Web Storage setItem 规则](https://html.spec.whatwg.org/multipage/webstorage.html#dom-storage-setitem)。不声称有跨窗口锁或断电耐久性；并发标签冲突、实机容量差异和真实 origin 尚待验证。首次写入需要临时额外空间，失败时不会先删除旧资料。

## 本次证据

2026-10-07 重建树重新运行构建、25/25 静态、56/56 单元（原 32 项 + 重建的 24 项存储/生产处理器故障注入），全部通过。新增的浏览器配额失败用例已恢复，但实际 Chromium 在 socket() 阶段启动失败，0 项断言执行；历史 126/126 不能替代本轮结果。

UI-011 已发布，[https://github.com/ForceMind/ai-phone-ui/actions/runs/37595281482](https://github.com/ForceMind/ai-phone-ui/actions/runs/37595281482) 的 exact-head CI 通过 25 静态、56 单元、127 浏览器回归。真实 origin/设备与配额验收仍开放；早先本地 socket 阻塞是历史环境限制。
