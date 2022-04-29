# -*- coding: utf-8 -*-
from gc import collect
from time import sleep, localtime, strftime
from win32gui import GetWindowText, GetWindowRect, GetForegroundWindow
from modules.ModuleGetTargetInfo import GetTargetPicInfo
from modules.ModuleGetScreenCapture import GetScreenCapture
from modules.ModuleHandleSet import HandleSet
from modules.ModuleImgProcess import ImgProcess
from modules.ModuleGetPos import GetPosByTemplateMatch, GetPosBySiftMatch
from modules.ModuleDoClick import DoClick


def time_transform(seconds):
    """
    转换时间格式 秒—>时分秒
    :param seconds: 秒数
    :return: 时分秒格式
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    run_time = "%02d时%02d分%02d秒" % (h, m, s)
    return run_time


def get_active_window(loop_times=5):
    """
    点击鼠标获取目标窗口句柄
    :param loop_times: 倒计时/循环次数
    :return: 窗体标题名称
    """
    hand_num = ""
    hand_win_title = ""
    for t in range(loop_times):
        print(f'请在倒计时 [ {loop_times} ] 秒结束前，点击目标窗口')
        loop_times -= 1
        hand_num = GetForegroundWindow()
        hand_win_title = GetWindowText(hand_num)
        print(f"目标窗口： [ {hand_win_title} ] [ {hand_num} ] ")
        sleep(1)  # 每1s输出一次
    left, top, right, bottom = GetWindowRect(hand_num)
    print("-----------------------------------------------------------")
    print(f"目标窗口: [ {hand_win_title} ] 窗口大小：[ {right - left} X {bottom - top} ]")
    print("-----------------------------------------------------------")
    return hand_win_title, hand_num


class StartMatch:

    def __init__(self, gui_info):
        super(StartMatch, self).__init__()
        self.connect_mod, self.target_modname, self.hwd_title, self.click_deviation, self.interval_seconds, self.loop_min, self.compress_val, self.match_method, self.scr_and_click_method, self.custom_target_path, self.process_num, self.handle_num = gui_info

    def set_init(self):
        """
        获取待匹配的目标图片信息、计算循环次数、时间、截图方法
        :return: 循环次数、截图方法、图片信息、每次循环大约需要执行的时间
        """
        # 参数初始化
        target_modname = self.target_modname
        custom_target_path = self.custom_target_path
        interval_seconds = self.interval_seconds
        loop_min = self.loop_min
        # 获取待检测目标图片信息
        print('目标图片读取中……')
        target_info = GetTargetPicInfo(target_modname, custom_target_path,
                                       compress_val=1).get_target_info  # 目标图片不压缩（本身就小）
        target_img_sift, target_img_hw, target_img_name, target_img_file_path, target_img = target_info
        print(f'读取完成！共[ {len(target_img)} ]张图片\n{target_img_name}')

        # 计算循环次数、时间
        t1 = len(target_img) / 30  # 每次循环匹配找图需要消耗的时间, 脚本每次匹配一般平均需要2.5秒（30个匹配目标）
        loop_min = int(loop_min)  # 初始化执行时间，因为不能使用字符串，所以要转一下
        interval_seconds = int(interval_seconds)  # 初始化间隔秒数
        loop_times = int(loop_min * (60 / (interval_seconds + t1)))  # 计算要一共要执行的次数

        return loop_times, target_info, t1

    def matching(self, connect_mod, handle_num, scr_and_click_method, screen_method, debug_status, match_method,
                 compress_val, target_info, click_deviation, run_status, match_status):
        """
        核心代码~
        :param connect_mod: 运行方式，windows或安卓
        :param handle_num: windows句柄编号
        :param scr_and_click_method: 是否兼容模式运行，两种方法不同
        :param screen_method: 截图方法
        :param debug_status: 是否启用调试模式
        :param match_method: 匹配方法、模板匹配、特征点匹配
        :param compress_val: 压缩参数，越高越不压缩
        :param target_info: 匹配目标图片
        :param click_deviation: 点击偏移量
        :param run_status: 运行状态
        :param match_status: 匹配状态
        :return: 运行状态、匹配状态
        """

        target_img_sift, target_img_hw, target_img_name, target_img_file_path, target_img = target_info

        # 获取截图
        print('正在截图…')
        screen_img = None
        if connect_mod == 'Windows程序窗体':
            handle_set = HandleSet(self.hwd_title, handle_num)
            if not handle_set.handle_is_active():
                run_status = False
                return run_status, match_status
            # 如果部分窗口不能点击、截图出来是黑屏，可以使用兼容模式
            if scr_and_click_method == '正常-可后台':
                screen_img = screen_method.window_screen()
            elif scr_and_click_method == '兼容-不可后台':
                screen_img = screen_method.window_screen_bk()

        # 支持安卓adb连接
        elif connect_mod == 'Android-手机':
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                screen_img = screen_method.adb_screen()
            else:
                print(device_id)
                run_status = False
                return run_status, match_status

        if debug_status:
            ImgProcess.show_img(screen_img)  # test显示截图

        # 开始匹配
        print("正在匹配…")
        pos = None
        target_num = None
        target_img_tm = target_img

        # 模板匹配方法
        if match_method == '模板匹配':
            if compress_val != 1:  # 压缩图片，模板和截图必须一起压缩
                screen_img = ImgProcess.img_compress(screen_img, compress_val)
                if debug_status:
                    ImgProcess.show_img(screen_img)  # test显示压缩后截图
                target_img_tm = []
                for k in range(len(target_img)):
                    target_img_tm.append(ImgProcess.img_compress(target_img[k], compress_val))

            # 开始匹配
            get_pos = GetPosByTemplateMatch()
            pos, target_num = get_pos.get_pos_by_template(screen_img, target_img_tm, debug_status)

        # 特征点匹配方法，准确度不能保证，但是不用适配不同设备
        elif match_method == '特征点匹配':
            if compress_val != 1:  # 压缩图片，特征点匹配方法，只压缩截图
                screen_img = ImgProcess.img_compress(screen_img, compress_val)
                if debug_status:
                    ImgProcess.show_img(screen_img)  # test显示压缩后截图
            screen_sift = ImgProcess.get_sift(screen_img)  # 获取截图的特征点

            # 开始匹配
            get_pos = GetPosBySiftMatch()
            pos, target_num = get_pos.get_pos_by_sift(target_img_sift, screen_sift,
                                                      target_img_hw,
                                                      target_img, screen_img, debug_status)
            del screen_sift  # 删除截图的特征点信息

        if pos and target_num is not None:
            match_status = True

            # 如果图片有压缩，需对坐标还原
            if compress_val != 1:
                pos = [pos[0] / compress_val, pos[1] / compress_val]

            # 打印匹配到的实际坐标点和匹配到的图片信息
            print(f"匹配成功! 匹配到第 [ {target_num + 1} ] 张图片: [ {target_img_name[target_num]} ]\n"
                  f"坐标位置: [ {int(pos[0])} , {int(pos[1])} ] ")

            # 开始点击
            if connect_mod == 'Windows程序窗体':
                handle_set = HandleSet(self.hwd_title, handle_num)
                handle_set.handle_is_active()
                handle_num = handle_set.get_handle_num
                doclick = DoClick(pos, click_deviation, handle_num)

                # 如果部分窗口不能点击、截图出来是黑屏，可以使用兼容模式
                if scr_and_click_method == '正常-可后台':
                    doclick.windows_click()
                elif scr_and_click_method == '兼容-不可后台':
                    doclick.windows_click_bk()

            # 支持安卓adb连接
            elif connect_mod == 'Android-手机':
                doclick = DoClick(pos, click_deviation)
                doclick.adb_click()
        else:
            print("匹配失败！")
            match_status = False

        # 内存清理
        del screen_img, pos, target_info, target_img, target_img_sift, screen_method  # 删除变量
        collect()  # 清理内存
        return run_status, match_status

    def start_match_click(self, i, loop_times, target_info, debug_status):
        """不同场景下的匹配方式"""
        match_status = False
        run_status = True
        connect_mod = self.connect_mod
        scr_and_click_method = self.scr_and_click_method
        match_method = self.match_method
        compress_val = float(self.compress_val)
        click_deviation = int(self.click_deviation)
        handle_num_list = str(self.handle_num).split(",")

        # 计算进度
        now_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        progress = format((i + 1) / loop_times, '.2%')
        print(f"第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次 \n当前进度 [ {progress} ] \n当前时间 [ {now_time} ]")

        # 多开场景下，针对每个窗口进行截图、匹配、点击
        if self.process_num == '多开' and connect_mod == 'Windows程序窗体':
            for handle_num_loop in range(len(handle_num_list)):
                handle_num = int(handle_num_list[handle_num_loop])
                print("--------------------------------------------")
                print(f"正在匹配 [{GetWindowText(handle_num)}] [{handle_num}]")
                handle_set = HandleSet(self.hwd_title, handle_num)
                handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
                handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
                screen_method = GetScreenCapture(handle_num, handle_width, handle_height)
                run_status, match_status = self.matching(connect_mod, handle_num, scr_and_click_method, screen_method,
                                                         debug_status, match_method,
                                                         compress_val, target_info, click_deviation, run_status,
                                                         match_status)

        # 单开场景下，通过标题找到窗口句柄
        elif self.process_num == '单开' and connect_mod == 'Windows程序窗体':
            handle_set = HandleSet(self.hwd_title)
            handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
            handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
            handle_num = handle_set.get_handle_num
            screen_method = GetScreenCapture(handle_num, handle_width, handle_height)
            run_status, match_status = self.matching(connect_mod, handle_num, scr_and_click_method, screen_method,
                                                     debug_status, match_method,
                                                     compress_val, target_info, click_deviation, run_status,
                                                     match_status)

        # adb模式下，仅支持单开
        # elif connect_mod == 'Android-Adb':
        else:
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                print(f'已连接设备[ {device_id} ]')
                screen_method = GetScreenCapture()
                run_status, match_status = self.matching(connect_mod, 0, scr_and_click_method, screen_method, debug_status,
                                                         match_method,
                                                         compress_val, target_info, click_deviation, run_status,
                                                         match_status)
            else:
                print(device_id)
                run_status = False
                return run_status, match_status

        del target_info, screen_method, connect_mod, scr_and_click_method, match_method, compress_val, click_deviation, handle_num_list  # 删除变量
        collect()  # 清理内存

        return run_status, match_status

    @staticmethod
    def time_warming():
        """检测时间是否晚12-早8点之间，这个时间可能因为异常导致封号"""

        if localtime().tm_hour < 8:
            now_time = strftime("%H:%M:%S", localtime())
            print("----------------------------------------------------------")
            print(f"现在 [ {now_time} ]【非正常游戏时间，请谨慎使用】")
            print("----------------------------------------------------------")
            for t in range(8):
                print(f"[ {8 - t} ] 秒后开始……")
                sleep(1)
            print("----------------------------------------------------------")
