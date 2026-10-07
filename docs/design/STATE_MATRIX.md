# 状态与恢复矩阵

状态检查和真实任务状态是两个不同维度。工作台的 default/empty/loading/error/offline 只切换共用视觉覆盖层，不调用网络或重置任务。

| 对象 | 主状态 | 用户看到 | 可执行控制 | 保留内容 |
| --- | --- | --- | --- | --- |
| 本机整理 | idle/running/paused/done | 确切原文进度和结果 | 开始、暂停、继续、结果 | 原文快照、处理索引、结果 |
| 真正远程任务（契约） | queued/running/needs_approval/paused/failed/completed/cancelled | 服务回执 | 由adapter明确支持 | taskId、步骤、版本与幂等键 |
| 服务连接 | disconnected/authorizing/ready/expired/error | 本版始终未连接 | 仅检查UI与范围 | 本机偏好，不保存凭据 |
| 图片 | original/derived/selected | 当前版本及源关系 | 比较、调整、裁切导出 | 原始像素与操作链 |
| 表单 | draft/invalid/reviewing | 当前输入，不自动提交 | 编辑/审阅/取消 | 路由+字段草稿 |
| 确认 | pending/consumed/cancelled | 固定对象、收件方、版本 | 左接受/右取消 | 不变的payload |
| 备份 | selected/invalid/review/restore | 替换范围 | 拒绝/确认 | 校验成功前保留旧资料 |
| 存储 | available/denied/quota | 可见告警 | 继续临时使用、导出 | 内存内状态 |

## 不能折叠的区别

“任务已停止输出”不等于“外部动作已经撤销”；“下载已交给浏览器”不等于“文件已成功落盘”；“用户勾选使用意向”不等于“设备已授予许可”；“本机预览确认”不等于“对方收到消息”。

## 组件状态范围

common empty/loading/error/offline 可复用，但相机拒绝、余额不足、删除、待审批各有独立页面。不要用一个通用错误弹窗覆盖所有业务风险。锁屏与息屏不要求展示所有工作台状态；检查重点是内容界面。

## 必须补验

真实断网、丢包、超时、中途关闭、存储配额满、大图内存压力、双击确认、恢复损坏备份、软键盘出现、系统边缘手势竞争。当前测试范围详见 QA 报告，未測项不得写成已通过。

CLD-17 / SET-10 恢复失败：原资料和确认保持，可重试或取消，不 reload。成功才提交同一快照，不表示云端同步。
