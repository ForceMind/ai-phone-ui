# 原始源码与历史恢复

本次采用用户批准的“源码快照 + 原始历史包”同步方式。在远端已有提交 `e5c33cbadedebcc4fb8f4d09132045f907bd7af0` 后新增普通提交，保留原有 LICENSE 和提交历史。原来的五次提交及注释标签保存在此目录的 bundle 中，**没有导入 GitHub 的提交祖先图，也没有重新创建同名远端标签**。

## 完整性

- 原始 ZIP SHA256：`0fcfeda117f705a210c54ca2608b318de18432e8f3709ed88fd597dba246c7b4`
- `project-history.bundle` SHA256：`76c662253478dbcf8946d3d40e8b4818a62fc48adbc11cffe46c83246f09e2f7`
- 原始 HEAD：`47b882b43b70750f250ff945aa2b7f0468bb0855`
- 原始提交数：5；原始跟踪文件数：156
- 原始 `v0.1.0-ui` 注释标签对象：`559456f86899df04fe2354c55d66bae047769c5e`；解引用为原始 HEAD

`project-history.bundle` 按字节原样保存，不是新生成的等价替代。源码快照在原始基线上包含 M0 文档、远端状态元数据与 CI 证据修正；原始版本仍可独立恢复。

## 安全恢复到全新目录

从当前仓库根目录执行，确保目标 `../ai-phone-original-history` 不存在。不要覆盖正在工作的目录，不要把恢复目录 force push 到本仓库。

```bash
sha256sum provenance/project-history.bundle
git bundle verify provenance/project-history.bundle
git clone provenance/project-history.bundle ../ai-phone-original-history
git -C ../ai-phone-original-history rev-parse HEAD
git -C ../ai-phone-original-history rev-list --count HEAD
git -C ../ai-phone-original-history rev-parse refs/tags/v0.1.0-ui
git -C ../ai-phone-original-history rev-parse 'refs/tags/v0.1.0-ui^{}'
git -C ../ai-phone-original-history status --short
```

依次应得到上述 HEAD、5、注释标签对象、解引用 HEAD，且工作区为空。恢复目录的 origin 是本地 bundle，不证明已与 GitHub 同步。

## 许可来源

本仓库根目录 LICENSE 按字节保留所有者预先创建的 AGPL 文件（Git blob `0ad25db4bd1d86c452db3f9602ccdbe172438f52`）。原始归档的占位许可通知另存为 `ORIGINAL_LICENSE_NOTICE.txt`，原始 package.json 标注 `UNLICENSED`；这些是历史事实，原始 bundle 未修改。

当前 package.json 通过 `SEE LICENSE IN LICENSE` 指向仓库现有文件。本次同步不宣称历史归档原本采用 AGPL，不新增第三方权利保证。交互参考与第三方名称的边界仍见 [来源](../docs/reference/SOURCES.md)。
