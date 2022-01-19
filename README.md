# SmartOmmyoji

> 为了解放双手，特意学了python，虽然已经有很多大佬写了类似的脚本，但自己主要是利用这个项目学习python，所以有很多被注释的代码片段和注释啥的

### 依赖库
- Gooey
- pywin32
- opencv-python
- numpy

### 使用
- 先安装python3.7,再安装上述依赖库
- 管理员身份运行 smart_onmyoji_gooey_ui.py
- 电脑版阴阳师不要调分辨率，如果要调分辨率，需要重新截图，放到对应的路径下面
- 支持后台点击，但好像应该不支持安卓模拟器，不过可以用scrcpy或qtscrcpy手机投屏连电脑，需要重新截图（opencv的模板匹配有点坑，大小方向一改变就匹配不到了。。。。）
- 原理是定时截图，然后找到图片坐标，然后随机延迟并点击附近随机坐标
- 除了阴阳师，也可以其他点点点的游戏，比如连手机抢微信红包啥的~
- 只要每天不刷满300次，理论上不会收到鬼使黑的信

### 计划
- 支持abd模式，电脑连手机自动截图，同时匹配模式改成opencv的特征点匹配方式（自适应分辨率，不用重新截图）
- 加载图片时记录所有图片的特征信息，优化识别速度
- 使用QT5重构UI界面
- 增加超时停止脚本的功能
- 优化百鬼夜行的选式神和砸豆子逻辑
- 模拟真实点击（某时间一顿猛戳，每隔一段时间随机等待30秒到5分钟）
- 增加御灵、地域鬼王、逢魔、秘闻副本等场景
