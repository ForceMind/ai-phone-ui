# 2026-10-08 · V4前景与任务呈现隔离候选

PR18测试先行a439cb7的run37738666668已确认新中断套件7/11：V4两画板在顶部菜单/锁屏接续后丢阅读位置，V3及照片几何均通过。当前候选只隔离挂载任务和系统前景的呈现属性，不缓存阅读位置、不扩大7页样板、不更改确认/资料/手势。保留RED及全部旧回归；必须重新核对候选自身完整CI、artifact、实图，再接入D2/D3。见docs/qa/V4_PRESENTATION_SUSPEND.md。

# D1 独立画板适配进行中

PR15的360×672浅深样板已按0ac9d00验证并交审。当前分支继续393×852实际布局/逻辑坐标适配，见docs/design/V4_VIEWPORT_ADAPTER.md；必须核验本分支自身CI与截图，不覆盖用户正在审阅的样板附件，也不提前进入D2/D3。

# V4 D0 / D1 接续 — 2026-10-08

当前已获准持续实施既有 iOS26 方案。方案原文见 `docs/design/V4_REDESIGN_PLAN.md`，执行门槛与回滚见 `docs/design/V4_IMPLEMENTATION_GATES.md`。PR13已合并main d164cdf并验证，PR14已进入eaf0874但Pages首次配置404；下方旧阶段文字作为历史保留。

本批新增可切换V3/V4浅深样板基础，尚不是完整D1或86页改版。下一步：候选exact-head CI、原回归、新样板截图与独立审阅；完善样板布局，再交用户确认视觉方向；独立质量工作持续推进。不得停止于首个样板提交。Pages设置、实机/读屏等未测边界单独保留。

---

# 开发交接入口

## 先恢复事实

读取 AGENTS、CURRENT_STATE 与 NEXT_ACTION；先检查工作区、实际远端 HEAD 和该 SHA 的 CI。源码基线 [dab0df96](https://github.com/ForceMind/ai-phone-ui/commit/dab0df965aab58636c893161c6d4a6ef205a948d) 和 UI-011 [8544894e](https://github.com/ForceMind/ai-phone-ui/commit/8544894e9c32511c9e3a03a47fe96c19ceaf7918) 已发布，不要再从“仓库只有 LICENSE”或“待恢复上传认证”继续。

## 当前实现

保留 V3 的三视图、Peek、活动封面、Pulley、固定快照确认、原片、草稿和单 HTML；86 页目录仍为唯一来源。UI-011 由 storage.cjs 在恢复时一次提交 core/suite，失败保持旧资料和可重试确认；不靠双写回滚假装原子性。

UI-011 原 CI 为 25 静态、56 单元、127 DOM fixture。[PR #7](https://github.com/ForceMind/ai-phone-ui/pull/7) 的测试提交 `e82370e342fabc83eacd1ca322b40a5b576a10f4` 另通过 14/14 HTTP-origin 原生存储回归，已核对实际 artifact。没有变更运行时 JS。旧 fixture 仍完整保留，真实 origin suite 单独启动 loopback server、导入文件、点击确认并观察生产 reload。当前 head 仍须复核自身 CI，不能用测试提交证据替代。实机、大图/OS 压力和并发标签冲突合并未证明。无外部服务连接或网站部署。

## 历史与接续

原 5 次提交/注释标签在 provenance 的原始 bundle 中，不在远端祖先图；根目录 LICENSE 原字节保留。先前工作区回退的恢复记载是历史，当前仓库可直接正常克隆。禁止 force push 或重建原始标签。

继续工作前运行 npm run build、npm run check、npm test、npm run test:ui、npm run test:storage；受限环境失败必须记录，不用旧报告替代。下一批仅按 [M2 卡](NEXT_ACTION.md) 验收现有确认页键盘焦点；设备验证仍开放，UI-011 整项仍不应提前关闭。

## 本批跟踪文字边界

PR #7 进入既定审阅/合并流程，代码与 main 合并结果需分别核对 exact-head CI。Testing Epic #1 的进度正文更新被取消，已保持原样；这只是未更新的跟踪文字，不阻塞已授权的独立代码 PR 收尾，也不应另写评论或重试该 issue 修改。

合并后测试时序记录：713e44b 的首次 main CI 暴露 native harness 提前导航（12/14），详见 QA 报告。测试须等待 core ready 与 Workbench 初始 deep link 都就绪；只等 core 标志会被延迟旧路由覆盖。保留失败证据，不能以 PR 通过代替 main 通过。

## 本批图像边界接续

PR #9 已保存 test-only 失败证据，再加入确认前的真实图片验证，保持原 URL 字节、16MP 启动限制及单快照提交协议。普通照片导入的 1400px 工作副本没有改动。单元的 Image mock 仅覆盖 14 个入口分支，不替代新增 5 个 native 图片场景。必须核对 [图像证据](../qa/UI011_IMAGE_EVIDENCE.json) 的对应 SHA，并在收尾时查最终 head 与 main 自身 CI。不要重新创建图像范围或将 UI-011 整项关闭；下一张卡仍位于 M2。


## UI-014 当前有界接续

PR #10 只收敛现有照片导入/导出与备份确认的键盘进入、取消和任务接续，保持明确接受路径及 UI-011 原片/16MP/原子恢复回归。先记录真实浏览器 RED，再修复焦点与原任务返回；文件选择启动超时和测试脚本点错恢复后菜单要与产品缺陷区分。见 UI014_FOCUS_EVIDENCE.json；最终 head 与 main 都必须各自核对 artifact。完整 UI-014 仍不关闭，读屏、大字及实际手机尚未验证。

独立代码阅读另提示：确认页可保留在任务会话中，而 pendingFile / pendingRestore 候选是全局变量，可能存在跨确认候选隔离缺口。该项尚未由原生浏览器复现；单独下一张有界卡调查，不把焦点修复当作已解决候选绑定，也不修改已取消更新的 Epic #1。


UI-014 的代码候选 `a3da630` 已经由独立审阅和真实 CI/artifact 验证：25 静态、84 单元、127 DOM、19 native 存储/图像、41 native 键盘。截图复核后仅纠正恢复确认按钮的动作名称，新增原生文案断言；最终 head 与合并 main 必须重新核对。不要在后续提交中丢弃已有 RED 与初版候选失败记录。


## PR #11 候选隔离接续

从已核对 main df55643 开始。d3430714 的真实 HTTP 测试已确认 pendingFile / pendingRestore 串用，而非仅代码怀疑；修复使候选随确认的共享对象保存，浅复制会话不会获得第二次执行权。取消先释放当前候选再恢复焦点，恢复只在 replace 成功后释放；失败保留同一候选。新增八项生产 handler 单元与六条 native 行为路径，详见 UI011_CANDIDATE_EVIDENCE.json。保留所有历史 RED，必须查最终 head/main CI，Epic #1 取消的文字更新继续不动。

候选 `28975e3` 的 run 37611856799 已核对通过 25/92/127/19/41/8；artifact ZIP、source-head 与预览 HTML 匹配。独立 review 无阻塞问题；最终小改仅撤去可选文件名显示、同步文档与登记验收，仍须自己的 CI，再核对正常合并 main。


## PR #12 当前接续：长确认阅读

[PR #12](https://github.com/ForceMind/ai-phone-ui/pull/12) 的 test-only `3491e207` 在真实 HTTP-origin Chromium 复现普通/大字长文不可滚读、无空格文本横向溢出以及键盘/纵向阅读失效；六条行为路径失败，异常/外部请求检查通过。首候选 `56d411b` 因继承文字选择使旧横滑取消回归失败（39/41），保留失败证据并只恢复原确认页的不可选择文字样式。

修正候选 `f16a9129aae5d4aeb483e2d67053cd33703ff5d9` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37639719218) 通过 25 静态、92 单元、127 DOM、19 native 存储/图像、41 native 键盘、8 native 候选及 8 native 阅读检查；ZIP、source-head 与三份构建文件字节已核对。普通/大字/不换行文本末尾、边界说明及跨任务阅读位置均有实际截图与几何证据。独立审阅无阻塞问题；最终像素收尾恢复原短确认标题颜色。见 [阅读证据](../qa/UI014_READING_EVIDENCE.json)。

这只是上述候选的通过结果。最终文档/样式 head 与正常合并 main 仍须分别核对 exact-head CI、artifact 和截图，不能沿用候选绿灯。完整 UI-014 仍开放，实际 Android/iOS、读屏、手机软键盘与 OS 字号未测；未调用真实消息/电话或外部服务。

产品改动复用既有 stack-scroll、手势分类与 sessions 阅读位置；新增读取键只作用于拥有焦点的当前确认。接受/取消处理器、候选一次消费和持久化协议不动。所有旧测试逐字保留。Epic #1 取消的正文更新继续不动。后续按 NEXT_ACTION 收尾，不把新阅读回归当成整个 M2 已结束。


## DAY-05 动作名称有界接续

PR #12 已正常合并为 main `a287cf068fccd8cc2b0b25b2bab8548b2bb7ec50`。最终 head `6323a2dd` 的 run 37641154241 与 main push run 37642165642 各自通过 25/92/127/19/41/8/8；两份 artifact 的摘要、source-head 和三份构建字节独立核对，main 七张阅读图与最终 head 像素相同。完整记录见 UI014_READING_EVIDENCE.json；以下此前的“待最终/main”属于保留的历史阶段。

当前独立有界卡只纠正 DAY-05 消息确认的动作名称：原按钮「确认导出」与真实行为不符，改为「确认本机预览」。该误导名称已在上一张卡的 main 实际截图中确认；不改变确认标题、固定接收方/正文、取消保留草稿、一次接受、候选归属或 local-preview-only 记录。没有发送消息、导出文件或新增服务副作用。

现有 HTTP-origin 阅读测试只加一条精确按钮名称断言，复用普通/大字/不换行文本、键盘取消、手势取消、接续与一次接受路径；不增加重复测试矩阵。全部旧断言保留。本卡还需自身 exact-head CI/artifact/截图、独立审阅、正常合并及 exact-main 复核。

完成后只交回 M2 剩余设备/读屏边界，不启动新的逐字修整。PR #12 合并后正文更新未确认成功并已停止；不重试、不另写评论。
