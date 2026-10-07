# v0.1.0 验证记录

## 2026-10-07 UI-014 长确认阅读

[PR #12](https://github.com/ForceMind/ai-phone-ui/pull/12) 的 test-only `3491e207` 在真实 HTTP-origin Chromium 复现普通/大字长文不可滚读、无空格文本横向溢出以及键盘/纵向阅读失效；六条行为路径失败，异常/外部请求检查通过。首候选 `56d411b` 因继承文字选择使旧横滑取消回归失败（39/41），保留失败证据并只恢复原确认页的不可选择文字样式。

修正候选 `f16a9129aae5d4aeb483e2d67053cd33703ff5d9` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37639719218) 通过 25 静态、92 单元、127 DOM、19 native 存储/图像、41 native 键盘、8 native 候选及 8 native 阅读检查；ZIP、source-head 与三份构建文件字节已核对。普通/大字/不换行文本末尾、边界说明及跨任务阅读位置均有实际截图与几何证据。独立审阅无阻塞问题；最终像素收尾恢复原短确认标题颜色。见 [阅读证据](UI014_READING_EVIDENCE.json)。

这只是上述候选的通过结果。最终文档/样式 head 与正常合并 main 仍须分别核对 exact-head CI、artifact 和截图，不能沿用候选绿灯。完整 UI-014 仍开放，实际 Android/iOS、读屏、手机软键盘与 OS 字号未测；未调用真实消息/电话或外部服务。

本地 build/check/92 unit 通过；Chromium 在首个断言前遭遇 socket EPERM。未绕过系统限制，原生结果均来自上述官方 Actions。6 条行为 + 2 条环境检查的矩阵有界，原测试/许可证/来源历史字节不变。

## 2026-10-07 UI-011 图像缺陷复现

测试先行提交 `cbd799cb81183ed17d862230da75a4742b8ff623` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37602605392) 通过 25 静态、56 单元和原 127 DOM；native 为 17/19。准确 16MP 和图像占用的 quota 取消/重试通过，超过 16MP 与有效 base64 但不能解码的文件仍进入替换确认。实际 artifact 的 source-head 和 SHA256 已校对。该失败保留在 [图像证据](UI011_IMAGE_EVIDENCE.json)，不能用后续绿灯抹去。

修复在恢复确认前验证解码/尺寸，保留原片；本地 build、25 静态和 64 单元通过。当地 Chromium socket EPERM 仍在首次断言前阻止启动，未绕过安全策略；真正浏览器验收通过正常 GitHub CI。图片修复提交 `ab06fa90e955c1664ad0f86d4abafc73785440ff` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37603387322) 已通过 25/64/127/19，artifact 摘要与 source-head 已核对。独立审阅随后发现过时解码可在最小化/锁屏后弹回确认：使用实际生产导航函数的单元复现为 8 通过/6 失败。后续修复仅在既有 captureSession 边界使请求序号失效，保留原会话保存；本地 70 单元通过。此后续修复与最终文档提交必须再核对 exact-head 及 main CI，不能沿用 ab06 的绿灯。

## 合并后发现的测试就绪竞争（2026-10-07）

PR #7 合并提交 `713e44be072462c41fded92fa76ad370f76ff17a` 的 [首次 main CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37600514374) 为 25/25 静态、56/56 单元、127/127 DOM，native 12/14。两项迁移测试已完成恢复与 reload 的数据断言，随后切往 DOC-02 时等待 `#noteEditor` 超时。不能把此前 PR 的成功当作这次 main 成功。

原因是新 harness 只等 core 的 `ready`，未等 Workbench 以 50ms 调度完成 URL 初始路由恢复；快速 runner 上，旧 SET-10 路由可能晚于测试的 DOC-02 导航而生效。修正仅在测试中显式使用 SET-10 deep link，并在每次真正 reload 后同时等待核心就绪、预期 Suite 路由和可见 URL hash。没有增加睡眠/重试、删除断言或模拟 Storage/reload，也没有修改产品运行时 JS。后续修正提交及合并后的 main 必须各自取得新的完整 CI。

## UI-011 真实 HTTP-origin 候选（2026-10-07）

[Draft PR #7](https://github.com/ForceMind/ai-phone-ui/pull/7) 的 `e82370e342fabc83eacd1ca322b40a5b576a10f4`：[Actions](https://github.com/ForceMind/ai-phone-ui/actions/runs/37598633407) 25/25 静态、56/56 单元、127/127 原 DOM fixture、14/14 新 native-origin 全部通过。Chromium 143.0.7499.4，Ubuntu 24.04.5，Python 3.13.15，Node 22.23.3。artifact 下载 SHA256 和 source-head 均已核对，详情见 [机器可读证据](UI011_ORIGIN_EVIDENCE.json)。

真实 origin suite 使用现有回环 HTTP 服务和浏览器原生 localStorage，执行真实 file input、确认按钮及整页 reload；不模拟 setItem/PhoneStorage/reload。四个配额探针各 25 次有界写入，实际填入 5,241,281（legacy）/5,240,987（snapshot）个字符并收到浏览器 QuotaExceededError。失败保留旧 bytes/内存与可重试确认，取消及释放测试 filler 后重试都通过。普通 core/suite 保存互不覆盖。没有暴露新的运行时恢复缺陷。

本地 Chromium 启动仍遇到 socket() EPERM，0 项 native 断言；没有改变安全策略。以上成功来自正常 GitHub runner，不能用本地历史结果替代。证据只覆盖这个明确 SHA；文档/目录验收元数据的新提交仍需新的 exact-head CI。

大图/设备内存、Android/iOS、OS 磁盘压力、HTTPS 部署、相机/麦克风权限、并发标签冲突及实际辅助技术尚未验证。以下较早的“未测真实 origin”描述仅属于历史批次。

## 当前远端发布验证（2026-10-07）

- M0 `dab0df965aab58636c893161c6d4a6ef205a948d`：[Actions](https://github.com/ForceMind/ai-phone-ui/actions/runs/37594652789) 成功，24/24 静态、32/32 单元、126/126 浏览器
- UI-011 `8544894e9c32511c9e3a03a47fe96c19ceaf7918`：[Actions](https://github.com/ForceMind/ai-phone-ui/actions/runs/37595281482) 成功，25/25 静态、56/56 单元、127/127 浏览器
- 两次均先删除历史结果，日志及 artifact 对应具体 source HEAD；新增恢复配额失败测试已在新运行通过

这是正常 GitHub Chromium 的新 DOM fixture 结果，不是复用旧 126/126。以下保留本地恢复和原归档记录作为历史；不得用它们替代后续提交的 exact-head CI。真实 origin、Android/iOS、权限、配额/大图仍待实测。


## 2026-10-06 重建候选验证

实际重建树重新执行 build、静态 24/24、单元 32/32，全部通过。构建为 238505 字节，SHA256 `db8ab10be7af577c55d465c062db477c4dc0911921ca91cd23c69436b7ec2fe3`。原始 ZIP、bundle 和 UI 行为源码精确恢复，文档/CI 修改重新生成。此前本地 Chromium 在首次断言前因 socket 限制启动失败，执行 0 项；未把旧浏览器报告算作新成功。

该历史恢复时点的 GitHub CI 尚未核对，当前结果见顶部。远端 UI 测试是 DOM 注入与内存 storage fixture，不能代替真实 origin、权限或 Android/iOS 实机验收。

## 原始归档结果（历史，不计入本轮通过）

| 层级 | 结果 | 证据 |
| --- | --- | --- |
| 构建与静态规范 | 24/24通过 | static-results.json |
| Node纯逻辑 | 32/32通过 | unit-results.txt |
| 浏览器UI回归 | 126/126通过 | browser-results.json |
| 界面渲染 | 86/86登记页可挂载与定位 | route:开头的检查 |
| 浏览器异常 | 未捕获JS异常0个 | page_errors |
| 默认外发请求 | HTTP/HTTPS/WS/WSS记录0个 | network_requests |
| 发布脚本 | bash -n语法检查通过 | scripts/publish-github.sh；未执行真实创建 |
| GitHub Actions | 未运行 | 仅提交workflow文件；原始归档当时未建远端 |

测试环境：v22.16.0；Chromium 144.0.7559.96 built on Debian GNU/Linux 13 (trixie)；Python Playwright按requirements-dev.txt。记录时间由运行环境生成：2026-10-04T16:46:26.132025+00:00。

## 浏览器测试确切方式

运行环境禁止file://与localhost导航；测试没有修改管理员策略。采用Playwright set_content把完整HTML加载到页面，成功路径使用显式内存localStorage fixture，另一个页面测试存储拒绝后的告警和继续编辑。触摸使用CDP事件，代表浏览器模拟触摸，不是手持设备。

## 行为覆盖

包括：86页目录、鼠标Pulley执行/取消/固定、Peek反转保留草稿、最小化再进入、内部返回、封面控制同一整理任务、顶/底边层、子页Pulley、嵌套任务父页、记下写入笔记、表单草稿、日程/周期草稿、固定消息快照与取消、选择性删除撤销、搜索、清单勾选、实际PNG/JSON下载、错误备份不覆盖、有效备份进入确认后可取消、无默认底栏、主题传递、状态检查、输入焦点快捷键、移动目录、设备适配、touch cancel和滚动冲突。

过程中修正了测试选择器与实际属性不一致的问题；最终测试未删除失败断言，而是使用真实页面属性定位并保留行为校验。补充了子层级任务页面、静态描述行语义与快照纯逻辑校验。

## 图像检查

输出86个默认首屏截图与全界面atlas，工作台可直接检查所有可操作页。人工查看了12个代表性界面总览和8个异常界面，未观察到这些默认首屏的标题/主要恢复入口重叠。长内容仍需滚动，不把截图高度之外的内容当成不存在，也不声称逐行全量人工审查完成。

## 未测试 / 不能据此推断

- 真实Android/iOS硬件、系统边缘竞争、软键盘、读屏、真实触觉。

- 真实file-origin或HTTPS部署的持久存储、配额压力和确认恢复后的整页reload；本次只测结构校验/拒绝/确认取消和纯模型roundtrip。

- 摄像头、麦克风真实许可与设备差异。

- 真实LLM、生图、Android云端、OAuth、消息、电话、计费等外部服务。

- 远端Git、PR、Actions或网站部署。

这些是后续M2/M4验收任务，不应隐藏在“全绿”或“UI完成”的表述里。全部登记UI完成按项目明确范围计，不是生产系统完成声明。

## 2026-10-07 重建后验证

构建通过；静态 25/25；单元 56/56。真实 Chromium 启动在 socket() Operation not permitted 处失败，退出 1，0 项断言。Node VM 故障注入不是浏览器或实机验收；保留的 126/126 是历史报告。该本地记录当时没有新远端 CI，当前结果见顶部。


## UI-014：有界确认键盘回归

测试先行 `a7b8fde` 记录 25 个直接焦点/取消返回失败与 7 个原生选择器启动超时；初版候选 `8e08e6b` 新键盘 suite 为 30/41，保留完整失败 artifact。嵌套确认焦点、测试点击已恢复的 Pulley 和选择器监听时序分别修正，不减少既有断言或重试到成功。

`a3da63073cd399745117be456ef57293795a6c95` 的 [run 37608195038](https://github.com/ForceMind/ai-phone-ui/actions/runs/37608195038) 实际通过 25 静态、84 单元、127 DOM、19 native 存储/图像与 41 native 键盘。ZIP SHA256、source-head、预览 HTML 与截图均已复核。这里的计数只适用于该 SHA；最终文案小改与合并 main 必须分别复跑。证据与未测边界见 [UI014_FOCUS_EVIDENCE.json](UI014_FOCUS_EVIDENCE.json)。


## M2：导入候选隔离

[PR #11](https://github.com/ForceMind/ai-phone-ui/pull/11) 首个测试提交 d3430714 的 [run 37611026086](https://github.com/ForceMind/ai-phone-ui/actions/runs/37611026086) 保持 25/84/127/19/41 通过，新增候选检查 3/7：两种旧备份确认提交 B、无效 B 使 A 不再提交，以及旧照片确认导入 B，均由真实浏览器确认。ZIP 摘要与 source-head 已核对。候选修复、最终 head 与 main 的结果按 SHA 单列在 [候选证据](UI011_CANDIDATE_EVIDENCE.json)，不能把某一绿灯外推。

候选 `28975e3` 的 run 37611856799 已核对通过 25/92/127/19/41/8；artifact ZIP、source-head 与预览 HTML 匹配。独立 review 无阻塞问题；最终小改仅撤去可选文件名显示、同步文档与登记验收，仍须自己的 CI，再核对正常合并 main。
