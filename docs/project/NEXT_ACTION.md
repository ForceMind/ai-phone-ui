# 下一步，只从这里继续

## 本批 UI-014：现有确认页的键盘焦点与取消

[Draft PR #10](https://github.com/ForceMind/ai-phone-ui/pull/10) 从 main `3299ba0217caa9850f39677aafd25eba9e3086f7` 开始。首个提交 `a7b8fde3f1fcbbc360245c971f9d2f88e2025c20` 只加入真实 HTTP-origin 键盘回归；先保存实际 Chromium 失败证据，再修复已复现问题。

- 范围：IMG-10 / IMG-01 的本机照片导入、IMG-02 的 Pulley 导出、SET-10 / CLD-17 的备份恢复确认
- 验收：进入确认先聚焦取消；Tab / Shift+Tab 可达且不落入底层；Escape、键盘/鼠标取消、右滑取消恢复可见的原入口；最小化后重新打开保留确认与草稿
- 照片导入取消回到发起的任务；明确接受仍遵循现有照片导入流程。导出取消只在有效原上下文恢复现有 Pulley，不执行命令
- 保留 V3 手势、固定快照和所有既有回归，不新增页面、功能、常驻导航或架构层
- 退出条件：实际失败与修复证据、独立审阅、最终 exact-head CI、正常合并后的 main CI/artifact 核对。设备、读屏与移动软键盘仍不在本卡完成声明中

UI-011 合成图边界已通过 PR #9 合入上述 main；保留 [既有证据](../qa/UI011_IMAGE_EVIDENCE.json)。UI-011 整项继续开放，不把桌面合成图当实机内存或 OS 压力结果。Testing Epic #1 正文维持原样，不重试、不另写评论。

## M2 实际设备边界仍开放

- UI-010：Android 与 iOS 各至少一台，记录机型/OS/浏览器，检查系统边缘、软键盘、Peek 反转、重复与取消
- UI-011：实际设备容量/OS 磁盘压力、大图内存边界；并发标签冲突合并尚未证明
- UI-014：除本次有界键盘卡外，仍需读屏、替代操作、大字体和长文
- 不用 Node VM、DOM fixture 或桌面 HTTP Chromium 代替真实手机结果

现有 planning/issues.json 保留 24 项计划；六张 Epic 无重复映射 15 个既有未完成条目。M3/M4/M5 按原顺序后续推进，不重做 86 页、不连接真实服务或部署。
