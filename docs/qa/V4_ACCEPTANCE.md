# V4 候选证据

## D0 / 早期D1：03a03a0236b22ecb6367696b75fde0923c755474

- PR15；run37717834519首轮成功。原有静态/单元/DOM/原生存储、键盘、候选归属、阅读套件全保留并执行。
- 静态26、单元96；旧DOM127、storage19、keyboard41、candidate8、reading8，新增design5通过。
- artifact11525100195，ZIP SHA256 cfde02fe0b3a42b9b00253481bdfce8b06d3b403c3ea6338ef1744dfd574b264；下载摘要、source-head、dist/index.html与该源提交字节已核对。
- 实际截图发现：旧task/stack径向染色穿透浅色内容；原生场景通过并不证明视觉合格。该候选不是可交用户确认的最终视觉稿。
- 独立源码review发现dark+增强对比组合留下浅青强调色，需完整覆盖palette；外置控制条必须整页与小屏检查，不只截phone。

## 后续候选（尚未具有自己的CI证据）

移除样板旧染色、补完整高对比配色；加入整页图与390px控制条几何检查；主封面跨列、照片头部收敛、中性薄框。截图fixture换用内置生成风景，原1px图继续用于真实存储/状态回归，不修改业务实现来美化测试图。

以上修正必须执行新的exact-head CI、artifact核对、实际像素审阅；不能继承03a03a0绿灯。仍是D1候选，393×852适配和样板完整批准尚未完成。

本地Chromium在socket EPERM启动前失败，未绕过系统限制。实机、读屏、软键盘、系统字号和性能门槛未验收。

## 第二候选 eb5231e59465bc98f069c7072d0995d30051fa49

run37718261811首次通过所有旧套件及新增6项（含dark+增强对比与390px布局检查）。artifact11524268086 ZIP SHA256 32ab0112c5a114509ee4f19a56d15dfdb443b1ac44809c04bdc229f85a621184；摘要/source-head/HTML字节已验证。实际浅色确认已不受旧渐变染色；主对象、照片大画面及手机外置控制条可见。

截图样例清理未达到预期：运行中clear后reload被生产离页保存恢复，仍呈现存储测试的1px照片。不得修改生产保存流程来迎合截图；下一候选改为在全新浏览器上下文初始种入无图片source的视觉fixture，调用原有内置生成风景。状态不变测试继续使用原fixture。

## 第三候选 d9327da9e23ce918b13814d4063bf1a75e007c80

run37718681784首轮成功，artifact11524812862摘要067bad546e8d6bec6daebd8df26dbe8e16904d82d84d8420906877df5df80a11。ZIP、source-head、三份dist文件均逐字验证。实际照片/主页现在正确呈现内置生成风景，浅深任务与动态样板可审阅。

下拉截图尚可能在内部动画过程中采集：phone外壳稳定不代表taskSurface内部已稳定。下一测试提交等待该真实动画结束，检查每个固定菜单命令没有被taskSurface遮住，再拍图；不修改生产动画或手势。另记录5秒CI RAF基线并强制HTML≤300000字节。尚不声称真机60fps。

## 尺寸接续自查：照片选区几何

D1将photoStage从424增为480，但旧selectPhoto/renderPhoto仍硬编码424。局部生产handler测试在旧代码上复现V4中心点偏移及letterbox可选（424基线仍过）；原始本地RED输出保存在V4_GEOMETRY_RED.json；此处不是原生浏览器RED证据。该问题在交付HTML前被发现，未称样板完成。

修复使用实际容器clientWidth/clientHeight统一计算contain图片和选区环；点击通过实际bounding rect归一化。样板切换只重新投影已有ring，不重绘图片、不修改选区/版本/草稿。新增4项单元（基线424、V4480、letterbox、切换ring）及原生真实点击/切换/圆环几何验证；尚需新head CI。原手势阈值、原图与选区数据结构不变。

## 第五候选 e535bd6 原生结果

run37719463909：所有旧回归通过，新增design 7/8；照片几何项首个“请求中心=精确0.5±0.001”断言失败，尚未进入ring切换检查。失败artifact11524834438，ZIP摘要4f663cf06a8ad44588e10acdf4360fee5763dadfa0d579d3d84483260e7014c6已下载核对。不可将此轮写成通过。

后续测试记录浏览器实际click坐标，以独立计算的square contain几何核对归一化选区，同时限定实际click距请求中心≤1设备CSS像素，避免把浏览器整数click舍入与产品选区错误混同。不是放弃原中心/letterbox/ring要求；实际点击到选区的误差仍严格≤0.00001，ring及两次设计切换断言保留。尚须新CI确认真实失败原因。

## 第六候选 9b89877 实际点击证据

run37719887233完整通过26静态/101单元/127DOM/19存储/41键盘/8候选/8阅读/8设计。artifact11524894908摘要e2b860696470380821deb9687df38119988349489eda08397d89f665619884ba；ZIP/source-head/三份dist字节已核对。

实际click为(720,507)，独立期望图像点(0.499991686,0.497876648)，生产选区为(0.499991686,0.497876648)，归一化误差<4e-10。首轮精确中心断言确为浏览器click坐标舍入不合理；真实选区、ring切换及letterbox均通过。5秒CI前台RAF301帧，p95约16.8ms，>50ms为0；不是设备性能证书。

像素复核又发现旧媒体选区浅边与旧toast底色在浅色样板对比不足。下一最小样式修正为双色选区边及明确反色反馈，增加实际computed style断言；业务状态不动。交付前仍核对这一新head，不能沿用本轮绿灯。


## V4跨任务阅读位置：继承缺口修复

独立393×852适配测试在run37721895181/head4490b33复现：确认页收起→未样板笔记→回确认，scrollTop恢复值先受V3小字体内容高度裁剪，随后V4样式才启用。该风险也影响固定360×672的V4候选，不能用默认V3阅读回归代替。

修复只在原captureSession完成后、目标页面渲染和scrollTop恢复前准备目标呈现样式。保存旧任务时仍使用它原有样式，恢复目标时使用其正确样式；不改变payload、候选、存储或确认行为。在原design套件新增完整V4跨任务阅读/焦点/一次接受断言，原断言全部保留。已交付附件在新head正式CI通过后沿原Library身份更新。


修复首轮56ed79d/run37722727966仍在新增V4接续断言失败，旧套件通过。进一步定位：DAY-05属于DAY-04任务根，确认自身没有routeId；只看栈顶会把呈现route误回落到DAY-04。修正为确认继承其下面最近的suite页面route，并同时用于恢复前准备与恢复后事件/current()。新增4项路由归属单元和恢复后DAY-05原生断言，保留全部既有断言。新head待CI，不把初候选当修复完成。


## 放大照片的手势命中区域审计

后续审计发现chooseMode仍用旧y=148..572判断照片版本横滑。生产函数单元RED1/3：扩展照片上方区域不响应，旧y范围中的非照片目标也可能误判；系统边缘优先级仍正确。修复以实际photoStage祖先命中判断，保留方向、阈值和系统边缘优先级。新增真实pointer在旧y范围上方左右切两个版本且不打开页面的回归；固定画布和393均验证，不以点击选区回归代替横滑。


### 可见层与呈现同步

完整手势入口审计还补充H回任务、T系统层、A能力层、Esc关闭后的样板归属同步。原Workbench只覆盖显式路由和部分指针结束；键盘返回可能保留上一个非样板页样式。syncAccess只发可见状态通知，呈现层用一次microtask读取最终Suite.current()，不写业务状态/历史；恢复前prepareView仍负责避免阅读位置被提前裁剪。新增合并通知单元与键盘层级原生回归，保留输入优先级和所有旧断言。

## D2 native first candidate, preserved failures

PR17 head999f59c/run37738614077 passed all old/D1/viewport checks; new core suite7/10. IMG-08 full-width range inherited browser margin and overflowed its reading region. Candidate CSS removes only native range margin; original overflow assertion retained, with failure screenshot added. Note-flow test assumed a confirmation on ui:export-document, but source shows this existing action downloads directly; harness now checks actual downloaded bytes and unchanged source without changing production semantics. Photo fixed-version confirmation/cancellation and execution once/cancel assertions remain. ZIP11532643941 sha256 dcca0916f95ab846c809c56ee5972f6127127f876661b906a8cffaadc83a5813 preserved.

## 首轮完整候选与补充门槛

ffd9bf2/run37740717375全绿，artifact11532874640 SHA256 3716cb62d11bf4bae0ba92b62fd18cbc9481779af80cba72eff8b54597882389，source-head及dist三文件匹配。393浅深86路由矩阵174/174（包括零异常/零出网），本机三闭环10/10，呈现中断11/11。首轮状态层只查挂载、退出使用路由API；不能据此宣称真实恢复/取消已通过。后续增强改用真实状态主按钮、Esc/Enter/H，并验证遮挡、固定确认与原内容。

实际浅色图发现DAY-10说明继承V3淡色、DAY-12路线覆盖层对比不足；使用语义次要色及固定媒体前景修正，不改计时或路线语义。独立review指出产品contrast未关闭blur，补CSS与native断言。独立呈现偏好补刷新/拒写/恢复隔离/V3回退/系统主题/无效记录，需新head专项结果。

## 独立复核追加（本地候选，native待验证）

ffd9bf2的393浅深正常状态172张已经分组实看。SYS-04两主题“所有设置”与菜单说明重叠，浅色说明继承旧淡青；候选使用紧凑正常流和语义文字色、媒体白字，并增加360/393 footer几何及截图断言。

独立源审发现设计态顶层没有隔离底层确认。真实confirmationKey函数的本地测试先得到Tab handled=true（预期false）的RED，再以独立状态层阻断得到GREEN；此前chooseMode源码VM也仍能落入confirm。不能把这当已运行的native误接受报告。修复复用syncAccess统一inert，取消进行中手势，层内pointer/键盘隔离；关闭只恢复仍连接且非inert的DOM焦点，不缓存业务或阅读位置。native新增层上左滑、Tab、Enter、Escape保持原payload/阅读位置且不接受，回原确认后允许明确一次接受，尚待本head CI。

拒写反馈不再只藏在窄屏隐藏span：warning时强制可见；native增加390宽可见、与手机区域不重叠及真实截图。129单元与26静态通过，Python及浏览器内JS片段语法通过；真实native新增项未跑。

## 交付文件最后检查

补充test:prefs中的standalone-offline-file：直接以file://打开构建出的单HTML，不用set_content或HTTP包装；真实编辑笔记、收起接续并下载文字，记录截图及外部请求。该检查仅证明当前桌面Chromium的离线打开/本机交互/下载，不替代所有浏览器file-origin持久化或实机验收。运行时代码不因该补充改变，仍需最终head与main分别取真实结果。
