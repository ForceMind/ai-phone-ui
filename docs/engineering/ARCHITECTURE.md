# 架构与维护边界

## 零运行时依赖构建

`template.html + styles/* + data/* + image.js + storage.cjs + core.js + model.cjs + suite.js + workbench.js → scripts/build.mjs → dist/index.html`。

源文件可分开维护，但加载时按既定顺序组合一个脚本作用域；单文件因此可离线打开。不存在后端、数据库或生产构建服务器。开发Python服务器只用于静态预览。

## 模块责任

- `image.js`：内置素材和像素处理。

- `core.js`：被认可的V3外壳，输入仲裁、页面栈、封面、原片与本机任务。大量全局函数仍然存在，是刻意保留行为的增量迁移，不是理想架构终态。

- `model.cjs`：纯状态校验、搜索、清单、裁切几何、快照；Node测试共享。

- `suite.js`：86页中的扩展页面、UI状态和动作；通过明确包装已有函数，避免两套手势引擎。需要后续按域拆分，不要继续无限增大 switch。

- `workbench.js`：开发目录、规格、演示、共用异常覆盖层，不能进入消费者App运行逻辑。

- `screens.json`：唯一登记表；类型、父节点、模式可静态校验。

## 数据与存储

Core key `ai-phone-ui-core-v1`（schema3），suite key `ai-phone-ui-suite-v1`（schema1）。与V3原存储键隔离，避免不明迁移覆盖。窗口内session保存页面栈，localStorage保存可恢复资料与表单。

备份格式包含两个经过验证的数据块。外部图像URL被拒绝；只允许限定data URL；未来对大图应迁移IndexedDB/分块存储并增加配额与恢复策略。没有加密存储承诺。

## 当前技术债

全局函数包装和跨域状态引用需要逐步替换成明确的controller/store；CSS tokens仍为记录而非自动生成；不是所有页面都有独立业务状态机；恢复时不重建全部动态封面的排列；个别原生V3动作与工作台目录的精确子页映射需进一步统一。

在行为测试保护下重构，绝不能为了换框架破坏已认可手势。

恢复后由 storage.cjs 的单快照提交承载 core/suite；旧格式在首次成功恢复前兼容。见 [存储恢复](STORAGE_RECOVERY.md)。
