# 下一步，只从这里继续

## 本批 UI-011 真实 origin 回归

[Draft PR #7](https://github.com/ForceMind/ai-phone-ui/pull/7) 新增独立 HTTP-origin 原生 localStorage 测试，保留全部 127 DOM fixture。测试提交 `e82370e342fabc83eacd1ca322b40a5b576a10f4` 已通过 25 静态、56 单元、127 DOM、14 native origin；[证据](../qa/UI011_ORIGIN_EVIDENCE.json) 明确记录源 SHA、artifact、浏览器和真实 quota 探针。后续提交需要再查其 exact-head CI，不能把此报告当最新 head；PR 保持 Draft，不自动合并或部署。

本批没有发现新的运行时恢复缺陷，没有为凑进展修改产品 JS。双区原子提交、确认前不写入、成功 reload、格式/大小拒绝和真实配额失败后取消/重试均有自动化证据。UI-011 整项与 Testing Epic #1 继续开放。

## 下一张有界工作卡：UI-011 大图持久化边界

- 使用合成图片，不读取或上传私人照片；HTTP-origin 检查解码尺寸限制、原片/版本保存和 reload
- 分别覆盖接近尺寸边界、超过解码像素上限、合法但无法解码的图片以及图像占用下的存储失败
- 先取得失败证据，再仅修复影响原资料保留或恢复诚实反馈的缺陷；保留现有 25/56/127/14 回归
- 退出条件：每个场景有实际 Chromium 结果、原资料/草稿保留断言及新的 exact-head CI；不把合成图浏览器结果当手机内存测试

## M2 实际设备与无障碍仍开放

- UI-010：Android 与 iOS 各至少一台，记录机型/OS/浏览器，检查系统边缘、软键盘、Peek 反转、重复与取消
- UI-011：实际设备容量/OS 磁盘压力、大图内存边界；并发标签冲突合并尚未证明
- UI-014：焦点恢复、读屏、替代操作、大字体和长文
- 未测项如实记录，不能用 Node VM、DOM fixture 或桌面 HTTP Chromium 代替

现有 planning/issues.json 保留 24 项计划；六张 Epic 无重复映射 15 个既有未完成条目。M3/M4/M5 按原顺序后续推进，不重做 86 页、不连接真实服务或部署。
