# 官方参考与采用方式

这些是设计来源，不是本仓库已有能力证明。文中的阈值与配色属于本项目设计。

1. Nokia N9 announcement / 2011-06-21: https://blogs.windows.com/devices/2011/06/21/introducing-the-nokia-n9-all-it-takes-is-a-swipe/

   N9使用MeeGo；采用其三主视图与从应用边缘返回Home的系统空间思路。不要写成N9原生搭载Sailfish。

2. Sailfish gesture design: https://sailfishos.org/design/gestures/

   采用边缘Home、Peek、顶部控制、底部应用层、页面返回等思路；本项目底部改为目的/能力而非传统App Grid。

3. Sailfish UI documentation: https://docs.sailfishos.org/Develop/Apps/UI/

   参考活动封面、氛围、导航与Pulley。本文将不同历史时期设计融合，不声称逐版精确复刻。

4. Jolla historical user guide: https://jolla.com/guide/en/index.html

   早期封面滑动和拉绳操作参考。若页面失效，保留参考用途，不据此虚构现行平台实现。

5. Android gesture navigation: https://developer.android.com/develop/ui/views/touch-and-input/gestures/gesturenav

   用于识别Web/应用不能独占系统保留边缘的限制，必须实机验收。

6. GitHub CLI create repository: https://cli.github.com/manual/gh_repo_create

   用于出版脚本 `--private --source --remote --push` 参数核对；不表示本次已执行。

7. Playwright Python: https://playwright.dev/python/docs/intro

   测试工具安装和浏览器自动化基础；模拟器不替代真实设备。

自制资源：Canvas内置风景、SVG图标和示例文案。没有分发商业字体或原厂图标资源包。
