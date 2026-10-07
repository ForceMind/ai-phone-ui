# 发布与交付

先运行 npm run build、npm run check、npm test、npm run test:ui。dist/index.html 是生成的单 HTML，不手改；运行时零依赖。浏览器测试依赖见 README。

本仓库采用源码快照 + 原始历史包，在已存在 LICENSE 初始提交后正常提交。旧 publish-github.sh 只保留为历史建仓工具，不用于现有仓库；不 force push、不重制原始标签。

Actions 只构建、检查、测试和上传当次日志/静态产物；先清除历史结果，不自动部署、不申请 secret。必须核对 exact-head CI 和 artifact/source-head.txt。公开仓库不代表网站已部署，本批不启用 Pages 或发布 release。

0.1.x 维护 UI 基线；0.2.0 聚焦体验与模块化；真实能力接入按独立里程碑。不能称为已完成 Android 系统。
