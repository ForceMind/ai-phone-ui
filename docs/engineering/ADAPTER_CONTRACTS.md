# 未来能力适配契约（未实现）

UI 不驱动第三方图形界面点击；以结构化意图调用已授权能力。实现一个真实adapter时需在单独PR申请范围，不能把模拟器直接改成默认网络连接。

## 最小请求

`requestId, taskId, capability, inputArtifactRefs, userIntent, grantedScopes, deadline, idempotencyKey, requireApproval`。模型可以建议步骤，执行器验证参数、授权和幂等；返回真实receipt和artifact version。

## 结果与事件

统一分为 local_result / preview_only / remote_result。远程状态只能来自有效服务返回。事件包含 eventId、taskId、sequence、serverTime、status、step、outputs、error 与 canRetry，重复/乱序事件不能造成重复提交。

## 取消与暂停

取消请求收到ACK仅说明服务接受请求；若已不可逆执行，必须显示实际结果和补救方式。暂停处理和停止播报不同，分别记录。后台计划不能因为用户离开当前页而重新执行已提交步骤。

## 许可

请求范围最小化，明示向哪里发送哪份资料；OAuth等真实授权不在静态HTML中完成。个人输入、返回结果、资料版本都属于租户，服务端必须隔离。密钥留可信代理；不接受任意URL代理或把密钥塞进localStorage。

## 类型

`src/contracts/services.ts` 是设计契约，不参与当前运行，也不是已连接SDK。原型不收集密钥，不调用这些远程接口。

## 接入门槛

先以契约测试覆盖：未授权、过期、空输出、失败、超时、重复事件、重复确认、取消竞态、部分成果、费用超限；再选择一条真实流程，不能一次开启所有服务。
