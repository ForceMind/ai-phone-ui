# 当前交付状态 — 2026-10-09

PR21/22/23 已合并，D4 已验证的软件子集已交付。核对 main 为 `cbd74ae9ab8fb874a3d92153418c6d7385d4065f`，其 UI quality 两个 job 通过；GitHub Pages 已通过既有 Actions 部署，公开入口为 [AI Phone UI](https://forcemind.github.io/ai-phone-ui/)。精确 run、构建摘要与旧失败记录见 [远端交付证据](../engineering/REMOTE_STATUS.md)。

Android/iOS 实机、软键盘、系统字号、VoiceOver/TalkBack、设备内存/存储压力仍未验证，完整 D4/M2 保持开放。已有 41 条桌面原生焦点与 10 条核心流程通过，不重复桌面矩阵来代替实机验收。真实短信、电话、账号、模型和云手机接入仍是后续独立范围。

以下为保留的历史阶段记录；其中“候选”“待 main”“Pages 未部署/门槛开放”仅描述当时状态，当前交付以上述证据为准。本次仅维护状态文档，不更改应用、生成物、版本或部署配置。

# D4 原生结果正文对比修复 — 2026-10-08

PR23 测试先行 ea337dc 的 Chromium run 37792922596 确认原生结果正文空/实际完成状态：浅色及加强对比均 1.3805520821569766:1，低于正文 4.5:1；深色 11.427409389821817:1。保留原始 RED artifact 11557192198。此为独立正文问题，PR22 子页评论仍是未复现，跨任务及真正同任务返回读位验收继续有效。

最小候选仅让 V4 原生 result 页正文使用 --v4-text，不改 JavaScript、资料、确认、布局或字号。三种外观×空/实际完成状态沿用实际背景测量，详见 docs/qa/V4_NATIVE_RESULT_CONTRAST.md。候选必须经过自身完整 UI quality、独立实图检查、正常合并后的 exact-main 复核，才更新已交付的同一 HTML 文件并保留版本追踪。最终状态以 PR23 的精确 head/main 记录为准；实际设备、OS 字号、读屏及 Pages 门槛仍开放。

# D4 子页评论有界核验 — 2026-10-08

PR21的“CLD04同cloud重建后读位归零”评论未在实际Chromium复现。Test-only 31fb6f9/run37787714815两个job通过，原D4 50/50、新核验8/8：目录CLD04和Back实际属于ui-CLD-02包装页；原cloud session保留471，回原cloud或真正同cloud结果子页返回都471→471。详见docs/qa/V4_D4_CHILD_ROUTE_REVIEW.md及逐阶段证据；不称修复产品缺陷，不否定原跨任务验收。

仅保留测试与核验说明，运行时HTML/src不变，不重发同字节HTML。最终head/main仍各自核CI。子页截图的独立实心像素量测为浅色/高对比1.3806:1、深色11.4274:1，是另行处理的正文对比问题，当前路由检查不证明子页文字全面达标；不夹带新设计或扩大本卡范围。原设备/OS字号/读屏/Pages边界仍开放。

# D4 浏览器代表样本已验证 — 2026-10-08

PR21运行时代码 `ec5c716` 的 [UI quality run 37778706779](https://github.com/ForceMind/ai-phone-ui/actions/runs/37778706779) 两个job通过：26静态、134单元、完整既有native回归与独立D4 50/50。96个实际背景文字样本最低6.3734:1；393×852下浅深×玻璃/减少透明度/高对比，长确认、设置、任务详情真实200%字号可滚读，六组跨任务读位471→471。保存了原始RED、保守测量修正、具体方法、artifact摘要与独立审阅，见 `docs/qa/V4_D4_ACCESSIBILITY.md`。

修复仅为确认/任务详情空间分配、实际溢出任务沿用scroll手势、原session的jobScroll接续以及数字字体框正leading。配色、固定payload、接受/取消、业务持久化、离线边界不变。单HTML297285B。收口文档提交不改变已验证运行时；交付仍须核对最终head/main各自CI、artifact和图像，不能用候选绿灯冒充主线结果。

后续只保留原计划尚未验证的实际Android/iOS、软键盘、OS字号、读屏、设备性能/存储压力，以及D5 Pages/真实外部服务门槛。本批不关闭完整D4/M2，不声称86页全部无障碍达标，不继续追加桌面逐字修整。PR与主线的实际合并/交付状态以GitHub及最终验收报告为准。

# 本地复核补充 — 2026-10-08

129单元/26静态通过；新增窄屏拒写可见反馈、设计态底层确认输入隔离、SYS-04 footer几何/配色修正。首轮172张393浅深图已实看；这些追加改动仍需独立native CI及最终像素，不沿用ffd9bf2绿灯。远端和合并事实以实际PR/CI为准。

# V4 整合候选收口 — 2026-10-08

用户已确认D1方向并继续D2/D3。PR20保留原公开提交及PR18阅读分层修复，86编号/55本机/31未连接预览不变。首轮ffd9bf2的run37740717375全部通过，artifact11532874640摘要、source-head及三份dist已独立核对；浅深393矩阵174/174（172路由+2异常/出网检查），核心本机闭环10/10，中断11/11。此为准确的393路由/几何/设计态矩阵，不是全业务或全画板证书。

独立review后追加呈现偏好持久化、真实状态主按钮恢复与原生返回/取消、产品加强对比停用模糊；浅色专注说明/地图路线的像素可读性补齐。独立小键不进入业务备份，恢复业务不覆盖当前外观；拒写不阻断当前操作。128本地单元与26静态通过，新增native专项仍需本head结果。

下一步：完整exact-head CI、实际新截图和独立review；正常merge到main后独立核验push run/artifact，再更新同一HTML附件并关闭已被包含的Draft。D4实机/辅助技术、D5 Pages配置与真实外部服务不冒充完成。以下阶段记录按历史保留。

# 2026-10-08 · V4前景与任务呈现隔离候选

PR18测试先行a439cb7的run37738666668已确认新中断套件7/11：V4两画板在顶部菜单/锁屏接续后丢阅读位置，V3及照片几何均通过。当前候选只隔离挂载任务和系统前景的呈现属性，不缓存阅读位置、不扩大7页样板、不更改确认/资料/手势。保留RED及全部旧回归；必须重新核对候选自身完整CI、artifact、实图，再接入D2/D3。见docs/qa/V4_PRESENTATION_SUSPEND.md。

# D3 九组迁移候选 — 2026-10-08

D1视觉方向已获继续确认；当前继承D2的24页与原7页，按系统/首次使用、AI/影像/资料、云端/日常/设置/异常三批样式覆盖剩余55页。86编号与55本机/31预览分类保留。每页仍复用原action与状态，不扩大真实服务。此为待CI与像素检查的候选，不是86页已验收。

D3新增完整86×浅深路由矩阵：实际进入/返回、阅读区几何、四类设计状态显示/关闭、V3回退保持原文/图片/草稿/固定确认；每页正常截图与九组状态截图。不同组保留各自结构：锁屏/息屏、欢迎/隐私、对象会话、媒体、文档、任务与文件、日程/通话预览、设置和错误恢复。套用颜色本身不构成通过；须读实际结果并检查图像。

本地26静态/119单元通过；本地Chromium被socket EPERM阻止，native待CI。D1系统覆盖层阅读疑点由PR18独立复现；未解决不合并。D4物理设备/软键盘/读屏及D5在线部署门槛仍开放。

# D2 核心闭环候选 — 2026-10-08

用户已于 2026-10-08 确认继续采用首批浅色主方向并保留深色。D1视觉决定已通过；D1代码仍须独立复核和exact-main门槛。当前独立D2分支将照片/资料/执行相关24页加入原7页，合计31页候选；其余55页保持V3，待D3逐组迁移。

共享内容表面、来源/版本、正文、清单、比较和确认采用同一语义配色；全部原业务action、存储、候选、一性确认及原图逻辑保留。V3回退和主题切换不写业务资料。新增core_flows_test覆盖浅深每个新页、退出/回退、原文→本机整理→取消/实际下载、固定照片导出、导入候选取消接续、备份跨任务及本机执行确认。真实外部执行服务未连接，不能把本机预览闭环写成真实服务回执。

本地26静态/119单元通过；本机Chromium启动socket EPERM，native测试待本head CI，不冒称通过。独立D1复核提出系统覆盖层可能改变底层长确认阅读位置，需要最小native复现；未复现前不当成已确认缺陷。当前批次不部署、不绕过D4实机/读屏/软键盘门槛。

下一步：exact-head CI及实际截图，关闭任何新失败；完成独立审查、正常合并和exact-main复核，然后迁移剩余九组页面。Pages配置独立处理。

# D1 独立画板适配进行中

PR15的360×672浅深样板已按0ac9d00验证并交审。当前分支继续393×852实际布局/逻辑坐标适配，见docs/design/V4_VIEWPORT_ADAPTER.md；必须核验本分支自身CI与截图，不覆盖用户正在审阅的样板附件，也不提前进入D2/D3。

# V4 D0 / D1 接续 — 2026-10-08

当前已获准持续实施既有 iOS26 方案。方案原文见 `docs/design/V4_REDESIGN_PLAN.md`，执行门槛与回滚见 `docs/design/V4_IMPLEMENTATION_GATES.md`。PR13已合并main d164cdf并验证，PR14已进入eaf0874但Pages首次配置404；下方旧阶段文字作为历史保留。

本批新增可切换V3/V4浅深样板基础，尚不是完整D1或86页改版。下一步：候选exact-head CI、原回归、新样板截图与独立审阅；完善样板布局，再交用户确认视觉方向；独立质量工作持续推进。不得停止于首个样板提交。Pages设置、实机/读屏等未测边界单独保留。

---

# 当前状态 — v0.1.0

## 当前有界批次：DAY-05 本机预览动作名称

PR #12 已正常合并为 main `a287cf068fccd8cc2b0b25b2bab8548b2bb7ec50`。最终 head `6323a2dd` 的 run 37641154241 与 main push run 37642165642 各自通过 25/92/127/19/41/8/8；两份 artifact 的摘要、source-head 和三份构建字节独立核对，main 七张阅读图与最终 head 像素相同。完整记录见 UI014_READING_EVIDENCE.json；以下此前的“待最终/main”属于保留的历史阶段。

当前独立有界卡只纠正 DAY-05 消息确认的动作名称：原按钮「确认导出」与真实行为不符，改为「确认本机预览」。该误导名称已在上一张卡的 main 实际截图中确认；不改变确认标题、固定接收方/正文、取消保留草稿、一次接受、候选归属或 local-preview-only 记录。没有发送消息、导出文件或新增服务副作用。

现有 HTTP-origin 阅读测试只加一条精确按钮名称断言，复用普通/大字/不换行文本、键盘取消、手势取消、接续与一次接受路径；不增加重复测试矩阵。全部旧断言保留。本卡还需自身 exact-head CI/artifact/截图、独立审阅、正常合并及 exact-main 复核。

## 已关闭批次历史：长消息确认阅读

上一张候选隔离卡 PR #11 已正常合并为 main `2139d5e9a800b53dec890e1373c772eeeacc0432`，main run 37635186925 已核对 25/92/127/19/41/8 及 artifact。以下更早批次保留为历史记录。

[PR #12](https://github.com/ForceMind/ai-phone-ui/pull/12) 的 test-only `3491e207` 在真实 HTTP-origin Chromium 复现普通/大字长文不可滚读、无空格文本横向溢出以及键盘/纵向阅读失效；六条行为路径失败，异常/外部请求检查通过。首候选 `56d411b` 因继承文字选择使旧横滑取消回归失败（39/41），保留失败证据并只恢复原确认页的不可选择文字样式。

修正候选 `f16a9129aae5d4aeb483e2d67053cd33703ff5d9` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37639719218) 通过 25 静态、92 单元、127 DOM、19 native 存储/图像、41 native 键盘、8 native 候选及 8 native 阅读检查；ZIP、source-head 与三份构建文件字节已核对。普通/大字/不换行文本末尾、边界说明及跨任务阅读位置均有实际截图与几何证据。独立审阅无阻塞问题；最终像素收尾恢复原短确认标题颜色。见 [阅读证据](../qa/UI014_READING_EVIDENCE.json)。

这只是上述候选的通过结果。最终文档/样式 head 与正常合并 main 仍须分别核对 exact-head CI、artifact 和截图，不能沿用候选绿灯。完整 UI-014 仍开放，实际 Android/iOS、读屏、手机软键盘与 OS 字号未测；未调用真实消息/电话或外部服务。

## 已发布

2026-10-07 源码基线 [dab0df96](https://github.com/ForceMind/ai-phone-ui/commit/dab0df965aab58636c893161c6d4a6ef205a948d) 与独立 UI-011 修复 [8544894e](https://github.com/ForceMind/ai-phone-ui/commit/8544894e9c32511c9e3a03a47fe96c19ceaf7918) 已进入 main，并逐文件核对。保留原 LICENSE 初始提交和 LICENSE 字节，没有 force push。

86 个登记界面仍为 55 本机交互页、31 未连接服务预览页；保留 V3 三视图、Peek、活动封面、Pulley、原片和单 HTML。原始 5 次提交与 v0.1.0-ui 注释标签保存在 [不可变历史包](../../provenance/README.md)，未导入 GitHub 祖先图或重建远端标签。

## 已核对质量

- M0 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37594652789)：24/24 静态、32/32 单元、126/126 新浏览器回归
- UI-011 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37595281482)：25/25 静态、56/56 单元、127/127 新浏览器回归
- 已通过正常 Git clone 回读，历史包 SHA256 和 LICENSE blob 均匹配

这是对应上述提交的真实 Actions 结果。后续文档或代码提交仍应核对自身 SHA 的 CI；不能把旧报告直接当作最新成功。详见 [发布证据](../qa/PUBLICATION_EVIDENCE.json) 与 [测试报告](../qa/TEST_REPORT.md)。

## M2 / UI-011 真实存储证据

[PR #7](https://github.com/ForceMind/ai-phone-ui/pull/7) 的测试提交 `e82370e342fabc83eacd1ca322b40a5b576a10f4` 已由 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37598633407) 通过：25 静态、56 单元、原 127 DOM fixture，以及新增 14/14 真实 HTTP-origin 回归。真实文件输入、明确确认、原生 localStorage、整页 reload 和有界原生配额取消/重试均已执行；artifact 的 SHA256 和 source-head 已核对。没有修改产品运行时 JS。详见 [分层证据](../qa/UI011_ORIGIN_EVIDENCE.json)。本条对应明确提交，后续文档提交与合并后的 main 仍核对自身 SHA；最新合并状态以 PR 记录为准。

## M2 / UI-011 合成图恢复边界

[PR #9](https://github.com/ForceMind/ai-phone-ui/pull/9) 测试先行得到 17/19 native 结果：准确 16MP 和图像占用下配额流程通过；过大/不能解码的备份仍可进入旧确认。对应修复只在确认前验证图片加载、像素上限和解码，保留原片及原有持久化协议；新增 14 个入口单元处理边界与过时异步结果。[图像证据](../qa/UI011_IMAGE_EVIDENCE.json) 按 source SHA 区分失败、修复和最终核对，不以历史结果冒充新 HEAD。

## 尚未完成

UI-011 原子恢复代码已实现并通过自动化；HTTP-origin Chromium 的原生存储/配额回归已获得上述独立证据；实际设备大图内存、OS 磁盘压力、Android/iOS、系统边缘、软键盘和无障碍仍属于 M2。原 127 项 DOM fixture 与新增 14 项真实 origin 分开报告，均不代表实机结果。

模型、云手机、消息、电话、音乐、地图、OAuth、账单及日历账号均未连接；没有部署网站，也不是完整 Android 系统。存储本地且未加密，中心裁切/圆形选区不是语义抠图。下一张工作卡见 [NEXT_ACTION](NEXT_ACTION.md)。

## 计划映射

已从既有 backlog 建立六张 [Epic](../../planning/README.md)，覆盖 15 个未完成条目且无重复；没有扩大功能范围，也未创建远端 Milestones。


## M2 / UI-014 确认焦点与取消接续

[PR #10](https://github.com/ForceMind/ai-phone-ui/pull/10) 从 `3299ba0` 开始，首个测试提交在真实 HTTP-origin Chromium 记录 25 个直接焦点/返回失败和 7 个文件选择启动超时。修复候选 `a3da63073cd399745117be456ef57293795a6c95` 的 [CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37608195038) 已通过 25 静态、84 单元、127 DOM、19 native 存储/图像与 41/41 native 键盘检查；artifact 摘要、source-head、构建 HTML 字节和截图均已核对。历史失败、harness 修正与通过证据分开记录，见 [按 SHA 分层的证据](../qa/UI014_FOCUS_EVIDENCE.json)。

这不是所有后续 head 或 main 的绿灯证明；最终小改（包括将恢复按钮的旧「确认导出」文案纠正为「确认恢复」）与合并 main 各自仍需 exact-head CI/artifact。完整 UI-014 仍开放，读屏、大字与实际手机未验证。


## M2 / 现有确认候选隔离

PR #10 已正常合并至 main df55643；该 main 的 run 37609773189 已由合并门槛核对 25/84/127/19/41。下一张有界卡是 [PR #11](https://github.com/ForceMind/ai-phone-ui/pull/11)：测试先行 d3430714 真正复现较新导入覆盖旧确认的候选，见 [按 SHA 分层证据](../qa/UI011_CANDIDATE_EVIDENCE.json)。修复只使照片/备份候选随确认共享并一次消费，不更改存储协议或页面。UI-011 与完整 UI-014 仍开放；本卡最终 head、正常合并 main 及 artifact 仍分别按门槛核对。

候选 `28975e3` 的 run 37611856799 已核对通过 25/92/127/19/41/8；artifact ZIP、source-head 与预览 HTML 匹配。独立 review 无阻塞问题；最终小改仅撤去可选文件名显示、同步文档与登记验收，仍须自己的 CI，再核对正常合并 main。
