# SWIPE / AI — AI Phone UI

![SWIPE / AI](docs/assets/swipe-ai.svg)

[![UI quality](https://github.com/ForceMind/ai-phone-ui/actions/workflows/ui-check.yml/badge.svg?branch=main)](https://github.com/ForceMind/ai-phone-ui/actions/workflows/ui-check.yml)
[![Repository license](https://img.shields.io/github/license/ForceMind/ai-phone-ui)](LICENSE)

> 源码与 UI-011 恢复一致性修复已发布。UI 代码提交 [8544894e](https://github.com/ForceMind/ai-phone-ui/commit/8544894e9c32511c9e3a03a47fe96c19ceaf7918) 的 [GitHub CI](https://github.com/ForceMind/ai-phone-ui/actions/runs/37595281482) 通过：25 静态、56 单元、127 浏览器回归。原始五次提交/标签按字节保存在历史包中；没有部署网站或连接真实服务。

一套以 **N9 三视图 + Sailfish 边缘手势、Peek、活动封面、Pulley** 为基础的 AI 手机界面与交互项目。

**当前：v0.1.0 UI 原型 / 86 个登记界面 / 单文件离线预览。** 这是用户认可的 V3 的工程化延续，不是回到“聊天机器人 + 底部导航”。

> 本仓库采用完整源码快照 + 原始历史包。原来的 5 次提交及 v0.1.0-ui 注释标签可从 [历史包](provenance/README.md) 恢复，未导入 GitHub 提交祖先图。保留现有 LICENSE 初始提交，未部署网站。徽章读取真实状态；CI 证据见 [远端状态](docs/engineering/REMOTE_STATUS.md)。

## 立即体验

打开 `dist/index.html`。手机或电脑浏览器都可使用；不需要登录、安装依赖或输入 API 密钥。左侧目录 / 手机端“界面目录”可进入全部界面；右侧是设计检查面板，**不是手机系统的一部分**。

下载文件在应用内预览不执行脚本时，请保存后用浏览器打开。部分浏览器限制本地文件持久存储、相机或语音，原型会显示限制，不会声称授权成功。

首先试：进入照片 → 从左边缘推到一半再推回 → 完整推开 → 横滑整理封面启动任务 → 返回照片 → 在内容顶部向下拉，松手执行暖调。也可点击“手势演示”。

## 项目内容

- 86 个明确编号页面（55 本机交互页、31 未连接服务预览页）：系统、首次使用、AI 会话、影像、资料、云端任务、日常能力、设置及异常状态。

- 保留整套 V3 手势；状态、资料、草稿与当前页面分离。

- 本机照片调色、版本比对、中心裁切导出、笔记、清单、原文整理、专注计时、草稿及 JSON 备份。

- 模型、云端 Android、音乐服务、消息发送、电话、地图、计费等 **未连接**，相关页面明确显示预览状态。

- 设计工作台提供默认/空/加载/失败/离线检查；这是共用状态样式，不是 430 个独立业务页面。

- 文档、计划、QA、CI 配置与交接入口一起维护。

## 本地开发

```
# Node.js 22+ / Python 3.11+
npm run build
npm run check
npm test
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
npm run test:ui
npm run test:storage
npm run dev
# 可选：重新导出可浏览的项目文档
npm run docs
```

开发服务仅监听本机 `127.0.0.1:4173`。生产发布不需要 Node 服务，`dist/` 是静态文件；没有自动发布或遥测。

浏览器测试默认通过 DOM 注入运行，并显式采用内存存储成功路径与存储拒绝路径，方便在受限沙盒中复现。它**不证明**真实 file:// 持久化或实机权限行为。新增的 `test:storage` 则单独启动回环 HTTP 服务，以浏览器原生 localStorage、文件导入、明确确认和真实 reload 验证 UI-011；不会将两种测试的证据混用。设置 `CHROMIUM_PATH` 可选择已有 Chromium。

## 目录与事实来源

| 路径 | 用途 |
| --- | --- |
| `reference/` | 原封不动的已认可 V3 与 SHA256 来源记录 |
| `src/template.html` | 原型外壳 |
| `src/js/core.js` | 已认可手势、任务会话及本机能力；仍有待拆分的旧全局代码 |
| `src/js/suite.js` | 完整界面与本机动作 |
| `src/js/model.cjs` | 可独立测试的状态校验与纯逻辑 |
| `src/js/workbench.js` | 手机外的目录、状态检查、流程检查工具 |
| `src/styles/` | 基础外观、页面组件、工作台样式 |
| `src/data/screens.json` | **唯一界面目录**：编号、父级、状态与本机/预览边界 |
| `src/data/tokens.json` | 设计参数参考；改动需同步实际 CSS/手势实现并测试 |
| `src/contracts/` | 未来能力适配契约；不表示已有后端 |
| `docs/` | 产品、设计、工程、QA 与交接 |
| `planning/` | 原有里程碑、待办与六张已核对 Epic 的映射 |
| `dist/index.html` | 由构建生成的独立体验文件，请勿直接修改 |

## 继续工作之前

依次阅读 [AGENTS](AGENTS.md) → [项目宪章](docs/project/CHARTER.md) → [当前状态](docs/project/CURRENT_STATE.md) → [下一步](docs/project/NEXT_ACTION.md) → [交接](docs/project/DEVELOPMENT_HANDOFF.md)。

设计人员从 [界面总表](docs/design/SCREEN_CATALOG.md)、[手势规范](docs/design/INTERACTION_SPEC.md)、[用户流程](docs/design/USER_FLOWS.md) 开始。开发人员从 [架构](docs/engineering/ARCHITECTURE.md)、[测试计划](docs/engineering/TEST_PLAN.md)、[发布](docs/engineering/RELEASE.md) 开始。

## 继续维护此仓库

公开仓库已存在，不再执行历史建仓脚本。基于实际远端 HEAD 进行普通提交或既定 PR；不 force push、不重新创建原始标签。旧历史按 [恢复说明](provenance/README.md) 克隆到新目录。

完整入口：[文档索引](docs/INDEX.md) · [路线图](docs/project/ROADMAP.md) · [交接](HANDOFF.md)

## 设计来源与授权

本项目采用多个时期的交互概念，不是单一历史系统复刻。没有使用 Nokia/Jolla 的商标作为本项目名称，也没有复制其专有资源或字体。[来源与映射](docs/reference/SOURCES.md)。根目录 [LICENSE](LICENSE) 按字节保留仓库所有者已有 AGPL 文件。原始待定许可通知另行归档，原始 bundle 不变；不声称历史版本原本采用 AGPL，也不作第三方权利保证。
