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

## M2 独立真实 origin 回归（UI-011）

运行 `npm run test:storage`。测试用 `scripts/serve.py --port 0` 在回环 HTTP 地址启动本批 `dist/`，每个用例使用独立 Chromium context 与合成资料。初始化数据通过 Playwright storage_state 写入浏览器原生 Storage；不替换 localStorage、setItem、PhoneStorage 或 location.reload。

覆盖旧双 key 在启动/重载时不提前迁移；用户从文件输入导入并点击确认后，core/suite 一起成为快照，真正整页 reload 后照片原片、版本、笔记、两侧草稿都保留；后续普通保存不覆盖另一部分。已存在快照的再次恢复也单独验证。恢复不能启动整理、专注或周期任务，不能恢复伪造连接。

取消、损坏 JSON、不支持的版本、外链图片和超过 12 MiB 文件必须在写入前拒绝，并在再重载后保留旧资料。真实配额测试只在该测试 context 写一个合成 filler key，通过有界二分查找触发 Chromium 自己的 QuotaExceededError：最多 16 Mi 字符/26 次 setItem。分别测试旧双 key 和快照模式的重复失败、取消以及释放测试 filler 后重试；失败时逐字节比较全部应用存储 key，并比较内存状态。

这证明的是正常 GitHub runner 上的 HTTP-origin Chromium Web Storage 行为，不能外推到操作系统磁盘压力、真实 Android/iOS、HTTPS 部署、多标签冲突合并或大图设备内存。测试报告单独写入 `test-results/storage-origin-results.json`，记录 source_head、Chromium 版本、实际配额探针和未测边界；原有 127 项 DOM fixture 不变。

## UI-011 图像替换前校验

2026-10-07 测试先行的 PR #9 在真实 HTTP-origin Chromium 发现：有效 data URL 结构并不能保证图片可解码。超过 1600 万像素及有效 base64 但不能解码的内容都可进入旧恢复确认，若提交后启动再拒绝图片，已经丢失原来的工作区。见 [失败与修复证据](../qa/UI011_IMAGE_EVIDENCE.json)。

修复只在恢复入口加入浏览器加载、既有 16MP 尺寸上限和完整解码校验，之后才建立 pendingRestore / 明确确认。保留 source 字节，不把原片替换成缩略图；空 source 的示例备份继续有效。序号与原页面身份避免异步结果覆盖较新选择；已有 captureSession 边界使离开、最小化和锁屏前的解码失效，即使再返回同一页面也不能弹回旧确认。单快照提交、quota 重试与清理协议未变。

原 14 项 native 回归保持，增加 5 项：4000×4000 准确边界确认/重载、4001×4000 拒绝、有效 base64 无法解码拒绝、超过 1 Mi 字符的真实噪声 PNG 占用下 legacy 取消/重载、snapshot 重试/重载。探针仍只操作测试 filler；每例关闭隔离 context。14 项额外单元仅证明加载/解码失败和异步陈旧结果控制，不能替代真实浏览器。桌面合成图的结果不证明手机内存或 OS 磁盘压力。
