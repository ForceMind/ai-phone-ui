# 测试计划

## 分层

1. 静态：目录编号唯一、父链有效、渲染类型存在、动作入口可解释、schema/manifest一致、无未替换构建标记、无外链脚本/样式、文档齐备、V3哈希不变。

2. 单元：状态校验、裁切范围、提取语义、搜索、数据限制、快照不可变、备份不能恢复伪造连接或周期启用。

3. 浏览器：全部86路由挂载；鼠标和模拟触摸检查边缘、Peek、Pulley、返回、封面、确认；真实本机表单/下载；网络请求和JS异常捕捉。

4. 真实设备：Android/iOS/桌面浏览器，系统边缘、软键盘、读屏、触觉、相机/语音拒绝、本地文件保存与大图。

5. 未来服务：adapter契约、权限、幂等、费用、断线恢复。当前没有远程服务，不能报告这层通过。

## 当前浏览器执行方式

历史受限环境的原回归采用 DOM fixture。`npm run test:ui` 通过 `page.set_content` 加载完整HTML，没有修改管理员策略；成功路径显式使用内存localStorage fixture，另一个页面保留存储拒绝行为。触摸是Chromium CDP事件，不是真实手机。

因此，路由与动作通过不等于已验证真实origin持久存储或全部手机权限。CI 配置本身也不等于对应提交已经运行成功。

`npm run test:storage` 是独立套件：从 `scripts/serve.py` 的回环 HTTP origin 加载实际构建产物，不注入 HTML、不模拟 Storage、不截获 reload。覆盖 native legacy/snapshot 数据、批准/取消、格式/大小拒绝及有界真实 quota 失败后取消/重试。每例独立 context，配额只消耗合成数据，结束关闭 context。参见 [存储协议与边界](STORAGE_RECOVERY.md)。

## 回归矩阵

每次手势改动至少：刚低于阈值、刚高于阈值、反向回推、pointercancel、开始在输入控件、已滚动子页、缩放视口、左/右侧、锁屏或弹层优先级。所有对外确认必须检查固定快照与取消不执行。

## 图像检查

比较同一尺寸截图；查看长正文滚动、遮挡、辅助文案、模态层和移动目录。`scripts/capture-ui.py` 可以输出实际运行画面的截图与总览，不能把静态截图当成可点击页面。

## 合并门槛

build/check/unit/browser均通过，未测项有明确记录；小范围改动也要复核全部登记页面可达。真实服务PR需新增服务测试和隐私审查。

UI-011 重建：17 项 storage 测试 + 7 项生产处理器 VM 测试，保留原 32 项。原 127 项 DOM fixture 已有远端证据；新的真实 origin 回归必须另行核对本批 exact-head CI。

UI-011 图像回归使用 Python 标准库生成有真实 PNG chunk/CRC 的 4000×4000、4001×4000 纯色图及 512×512 噪声图，不读取私人图片。原生报告记录像素、编码长度、fixture SHA256 与 quota 探针。拒绝前后比较实际存储 bytes/运行状态；成功及取消均检查 reload 后原片、版本和草稿。新增 `tests/backup_image.test.cjs` 的 Image 是明确的单元 mock，仅验证 14 个入口控制分支，原 56 单元、127 DOM 与 14 native 用例不删除。
