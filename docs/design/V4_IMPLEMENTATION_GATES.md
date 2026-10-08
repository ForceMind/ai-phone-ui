# 当前执行更新 — 2026-10-08

2026-10-08阶段决策已确认D1视觉方向，批准按浅色主方向并保留深色继续D2/D3迁移。下方早期D0/D1段落保留为阶段历史。当前PR20以正常merge保留PR15–19公开历史；D2三条本机闭环与D3全86页候选已有首轮准确提交CI，后续改动继续核自己的head。

首轮整合ffd9bf2/run37740717375通过26静态/125单元/127DOM/19存储/41键盘/8候选/8阅读/11设计/14画板/10核心/174矩阵/11中断。矩阵准确边界是393×852的86页浅深路由、阅读区几何与设计态挂载；不是86页全尺寸或全部业务验收。360覆盖原回归、样板及阅读中断专项；实机/软键盘/读屏/OS字号仍未测。

当前追加完善：设计态顶层可见与真实主按钮恢复、Esc/Enter/H退出；独立呈现偏好键（V3/V4、浅/深/跟随系统、透明度、画板）允许持久化，业务资料/确认/备份schema不变。拒写明确降级为当前窗口有效。加强对比度同时停用玻璃。新增native偏好专项与加强后的矩阵需要本head CI，不沿用上一提交绿灯。

# V4 实施衔接与门槛

2026-10-08，基线 eaf0874e887d3cad8dad4fbe60906475c1c81649。
用户已要求持续推进现有版本计划。`V4_REDESIGN_PLAN.md` 是既有提案的原文快照，不重写它、不把其中过去“未修改仓库”的描述当现在的状态。当前执行事实以本页与 CURRENT_STATE 为准。

## D0 / D1 当前边界

- 86 个编号、55 本机 / 31 未连接预览、既有路由和业务逻辑继续保留。
- D0：方案落库、样板界限、性能预算、玻璃降级与回滚标准。
- D1 首轮候选：设计检查工具提供 V3 / V4、浅 / 深、减少透明度。七个编号页（SYS-01/02/03、IMG-02、CLD-03、DAY-05、SET-01）及任务下拉组件构成八样板范围。
- 当前只是视觉基础候选，尚未达到完整 D1：主对象优先布局、动态分组、393×852 自适应、16 张验收主状态图及用户视觉确认仍待完成。不能据此宣布全量改版。
- 样板外页面明确回到 V3；不会将未迁移页面包装成 V4 完成。
- 样板外观仅驻留内存，不写主题、业务、任务或授权数据。退出样板不触发路由/确认/存储动作。
- D1 视觉方向确认后继续 D2 三闭环与共享组件、D3 其余页面、D4 真机与无障碍、D5 离线和在线交付。等待视觉决定时可继续独立回归和组件规则整理。

## 可执行性能预算（项目门槛，不是 Apple 参数）

D0 基线 HTML 249024 字节。D1 单 HTML 上限 300000 字节；超出必须说明资源增量与收益。保持零网络运行时依赖，无外部字体或 CDN。

CI 桌面 Chromium 记录浏览器/视口/source SHA；先量测而非承诺 60fps：
- 每次样板主题/材质切换产生零新增业务状态写入、零页面重载、零外部请求。
- 30 次主题/材质切换后 DOM 节点数量不得持续增长；设计工具只创建一次。
- 交互采样至少 5 秒；报告 RAF 间隔 p50/p95 和大于 50ms 的帧数。该数字仅作同环境基线，后台/CI 调度会影响它，不作为真机证明。
- D4 真机候选门槛：前台操作 RAF p95 ≤ 20ms、≥50ms 间隔占比 <1%；在记录的设备上测三轮，失败则先关闭玻璃再定位。低端设备未测不宣称达标。
- 不实现实时全屏折射；功能层最多一个模糊平面，模糊上限 12 CSS px；不用玻璃嵌套玻璃。正文、长确认、照片源像素不模糊。

## 玻璃降级

基础样式先提供高遮挡实色，只有浏览器明确支持 backdrop-filter 且未选择减少透明度时，功能层采用 12px 模糊。减少透明度、系统 prefers-reduced-transparency、增加对比度均停用模糊。深色与浅色分别定义前景/背景，不仅反色。

用户减少动效沿用现有全局规则；功能层不得新增不可关闭的循环装饰动画。浏览器不支持相关媒体查询时，仍可通过样板检查工具显式关闭透明度。后续 D2 将此规则接入产品级无障碍设置；不得声称当前样板开关已与 OS 设置完全同步。

## 回滚触发与步骤

触发：数据丢失、确认对象/一次消费改变、旧回归失败、无法退出/恢复、正文不可读，或样板性能预算超出且未解释。

1. 停止该批推广；保留失败报告、截图和精确提交。
2. 样板检查中立即选 V3，不清空 localStorage、不重建任务、不消费确认。该开关只撤销样式作用。
3. 若已合并，用普通 revert 撤回该批提交，经相同 CI 验证再正常合并；不强推、不改历史、不回退用户数据 schema。
4. 在线发布单独按授权和发布门槛恢复到最后验证的构建；不假定代码回滚等于 Pages 部署完成。
5. 修复后创建新候选，对相同 RED 场景及全部旧回归复测。不得删断言换绿灯。

## 发布与实机

PR13 main d164cdf 的 CI 已通过 25/92/127/19/41/8/8；此为历史基线，不是本批绿灯。
PR14 main eaf0874 只加 Pages 工作流；首次 run37646443486 Configure Pages 404，上传/部署跳过。Pages设置/登录仍独立待解决，不阻断D0/D1开发，不把未知网址当交付。
实机 Android/iOS、VoiceOver/TalkBack、软键盘、系统字体、真实内存/磁盘压力依然未测，D4不可提前关闭。

## Mounted task / foreground presentation boundary

PR18's confirmed interruption RED requires task presentation to remain tied to its content route through system menus, lock, and sleep. The candidate scopes content styles to `[data-design-surface][data-design-sample=true]`; the root's visible-route flag is diagnostic only. Approved D2/D3 style extensions must retain this surface qualifier, including self-target selectors for overlay/toast surfaces, and must not change the sample list merely to mask interruption failures. Reading offsets remain owned by the original DOM/session implementation, with no presentation cache. See the preserved RED and candidate details in `../qa/V4_PRESENTATION_SUSPEND.md`.

## D4 representative browser gates (PR21)

The bounded browser subset now has an independent test-only RED: 96 actual
composited-background samples pass, SET-01 text-only 200% reading passes, and
DAY-05/CLD-03 text-only 200% layout fails across six presentation combinations.
The layout candidate must pass its own old and new jobs, source/artifact readback
and screenshots. This does not close physical-device, OS-text-size or assistive
technology gates. See `../qa/V4_D4_ACCESSIBILITY.md`.

Runtime `ec5c716` subsequently passed the complete old regression job and all
50 D4 checks (run 37778706779), with actual artifact/pixel readback and independent
source review. The final docs-only head and merge main each retain their own
verification gate; this closes only the representative browser subset.
