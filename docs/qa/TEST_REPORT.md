# v0.1.0 验证记录

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
