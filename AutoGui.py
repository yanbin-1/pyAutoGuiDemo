import pandas as pd
import pyautogui
import time
import pyperclip
import os
import datetime


class GetRunNum:
    # 全局计数器
    __run_num = 1

    @classmethod
    def addRunNum(cls):
        cls.__run_num += 1

    @classmethod
    def subNum(cls):
        cls.__run_num -= 1

    @classmethod
    def getRunNum(cls):
        return cls.__run_num


def myLog(*BUF, log_method=1):
    # 输出到文件
    if log_method == 1:
        with open("./log.txt", "a") as log:
            print(datetime.datetime.now().strftime("%F %T"), file=log, end="\t")
            for i in BUF:
                print(i, file=log, end=" ")
            print("", file=log)

    # 输出到控制台
    elif log_method == 2:
        print(datetime.datetime.now().strftime("%F %T"), end="\t")
        for i in BUF:
            print(i, end=" ")
        print(end="\n")


def readCheckData(path: str) -> pd.DataFrame:
    # 读取数据，返回数据
    df = pd.read_excel(path, header=0)
    return df


def checkParseCommand(source_command: str) -> dict:
    """
    检查所给command格式是否正确并解析
    Args:
        source_command:

    Returns:

    """
    command_dict = {}

    source_command = source_command.replace("，", ",")

    # 格式错误
    if source_command.count(",") + 1 != source_command.count("="):
        myLog("{}有误".format(source_command))
        return command_dict

    # 格式正确 a = 1, b = 2
    # 将间隔符全部替换为"="
    source_command = source_command.replace(",", "=")
    command_list = source_command.split("=")

    # source_command中的奇数元素位命令，偶数元素为参数
    for i in range(0, len(command_list), 2):
        # 去除首位空格
        cur_command = command_list[i].strip()
        cur_param = command_list[i + 1].strip()

        # 存储
        command_dict[cur_command] = cur_param
    return command_dict


def detectImage(img_path, command_value):
    """
    检测屏幕中是否有图片
    Args:
        img_path:
        command_value:

    Returns:

    """
    while True:
        location = pyautogui.locateCenterOnScreen(image=img_path, confidence=0.95)
        if command_value == "出现":
            if location:
                break

        elif command_value == "消失":
            if not location:
                break

        time.sleep(0.1)


def detectFile(command_value, method=1):
    # 检测文件出现
    if method == 1:
        while not os.path.exists(command_value):
            time.sleep(0.1)

    # 检测文件消失
    if method == 2:
        while os.path.exists(command_value):
            time.sleep(0.1)


def executeCommand(img_path: str, command_dict: dict, interval: float) -> None:
    """
    根据给的那个参数执行相应逻辑命令
    定位图片中心、移动、偏移、左键、右键、中键、输入、按住、松开、检测（暂定给定图片检测出现和消失的瞬间）、
    打开软件、关闭软件、等待、区间内循环、检测文件是否出现，检测文件是否消失、新建文件夹
    当输入为"$inputNum"，则替换为全局计数器并加1，如果输入"$getNum"，则输入全局计数器
    Args:
        img_path: 图片路径
        command_dict: 命令参数{命令：参数}
            i.e., {左键：1， 中键：10，右键：-1}
        interval: 每个动作后的等待时间

    Returns:

    """
    # 是否可以移动到图片
    move_flag = True

    for command_key, command_value in command_dict.items():
        # 如果输入全局计数器
        if "$addNum" == command_value:
            GetRunNum.addRunNum()

        if "$subNum" == command_value:
            GetRunNum.subNum()

        if "$getNum" in command_value:
            input_num = str(GetRunNum.getRunNum())
            command_value = command_value.replace("$getNum", input_num)

        # show
        myLog("图片：{}，命令：{} {}".format(img_path, command_key, command_value))

        # 有图片路径
        if pd.notna(img_path) and os.path.exists(img_path):
            # 检测
            if command_key == "检测":
                detectImage(img_path, command_value)

            # 定位图片中心并移动
            elif move_flag:
                start = time.time()

                while True:
                    # 获得图片中心位置
                    location = pyautogui.locateCenterOnScreen(image=img_path, confidence=0.95)

                    if location:
                        location_x = location.x
                        location_y = location.y

                        # 移动到图片中心
                        pyautogui.moveTo(location_x, location_y)
                        move_flag = False
                        break

                    if time.time() - start > 10:
                        pyautogui.alert(text=img_path + "查找超时", title="错误")
                        return

                        # 移动（根据像素点移动）
        if command_key == "移动":
            # 获取目标点像素点
            coordinate = command_value.split("/")
            location_x = int(coordinate[0].strip())
            location_y = int(coordinate[1].strip())

            # 移动
            pyautogui.moveTo(location_x, location_y)

        # 偏移(根据像素点偏移)
        elif command_key == "偏移":
            # 获取目标点偏移量
            coordinate = command_value.split("/")
            offset_x = int(coordinate[0].strip())
            offset_y = int(coordinate[1].strip())

            # 偏移
            pyautogui.moveRel(offset_x, offset_y)

        elif command_key == "检测文件出现":
            detectFile(command_value)

        elif command_key == "检测文件消失":
            detectFile(command_value, 2)

        elif command_key == "输入":
            # 原本剪切板的内容
            text_backup = pyperclip.paste()

            # 输入内容复制进剪切板
            pyperclip.copy(command_value)

            # 输入
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)
            pyperclip.copy(text_backup)

        elif command_key == "按住":
            pyautogui.keyDown(command_value)

        elif command_key == "松开":
            pyautogui.keyUp(command_value)

        # 左键点击n次
        elif command_key == "左键":
            for _ in range(int(command_value)):
                pyautogui.leftClick()
                time.sleep(0.01)

        # 右键
        elif command_key == "右键":
            for _ in range(int(command_value)):
                pyautogui.rightClick()
                time.sleep(0.01)

        # 中键
        elif command_key == "中键":
            for _ in range(int(command_value)):
                pyautogui.middleClick()
                time.sleep(0.01)

        # 打开软件
        elif command_key == "打开软件":
            split_text = command_value.split("\\")
            root = "\\".join(split_text[:-1])
            name = split_text[-1]
            os.system("cd {} & start {}".format(root, name))

        # 关闭软件
        elif command_key == "关闭软件":
            os.system("taskkill /f /t /im {}".format(command_value))

        # 等待
        elif command_key == "等待":
            try:
                command_value = float(command_value)
            except:
                pyautogui.alert(text="等待时间请输入数字", title="错误")

            time.sleep(float(command_value))

        # 如果输入新建文件夹
        # 新建文件夹 = C:\yan\1-400
        elif command_key == "新建文件夹":
            root, names = command_value.split("\\")
            split_text = names.split("-")
            if len(split_text) != 2:
                pyautogui.alert(text="未指定起始终止文件夹", title="错误")

            try:
                start_name = int(split_text[0])
                end_name = int(split_text[1])

            except:
                pyautogui.alert(text="起始终止文件夹名称必须为整数", title="错误")

            if end_name < start_name:
                pyautogui.alert(text="终止文件夹不能小于起始文件夹吧", title="错误")

            # 创建文件夹
            [os.mkdir(os.path.join(root, str(name))) for name in range(start_name, end_name + 1)]

        # 等待
        time.sleep(interval)


def main() -> None:
    """
    主程序运行
    Returns:

    """
    # 指定excel路径
    path = input("请输入命令文件路径")
    if len(path) == 0:
        path = "./example.xlsx"

    # 手动输入参数
    part_cycle_start = -1
    part_cycle_end = -1
    part_cycle_time = -1

    while True:
        cycle_cmd = input("是否指定循环区间和循环次数/(Y/N)")
        if cycle_cmd not in ["Y", "y", "N", "n"]:
            myLog("输入错误，请重新输入")
            continue

        # 不需要循环
        if cycle_cmd in ["N", "n"]:
            break

        # 开始输入循环相关
        try:
            part_cycle_start = int(input("请根据所给excel所在行输入循环开始区间"))  # 从2开始
            part_cycle_end = int(input("请根据所给excel所在行输入循环结束区间"))
            part_cycle_time = int(input("请输入上述循环区间的循环次数"))

            if part_cycle_end <= part_cycle_start:
                myLog("结束区间需要大于开始区间")
                continue

            break
        except:
            myLog("请输入整数")

    # 指定整个excel的循环执行次数
    all_cycle_times = int(input("请输入整个excel的循环执行次数"))

    for cycle_time in range(1, all_cycle_times + 1):

        myLog("......................开始第{}次循环......................".format(cycle_time))

        # 读取文件
        df = readCheckData(path)

        # 输入的区间是从2开始的，这里减去方便索引
        part_cycle_start -= 2
        part_cycle_end -= 2
        i = 0

        try:
            while i < df.shape[0]:
                # 是否启动该行，当该值为0时不启动，其余情况启动
                enable_flag = df.iloc[i, 1]
                if enable_flag == 0:
                    continue

                # 解析文件列
                img_path = df.iloc[i, 2]  # 图片路劲
                times = 1 if pd.isna(df.iloc[i, 3]) else int(df.iloc[i, 3])  # 运行次数
                timeout_method = df.iloc[i, 4]  # 超时行为
                interval = 0.1 if pd.isna(df.iloc[i, 5]) else df.iloc[i, 5]  # 动作间隔
                source_command = df.iloc[i, 6]  # 执行动作

                # 允许空行
                if pd.isna(source_command) or len(source_command) == 0:
                    continue

                # 检查并解析command格式
                command_dict = checkParseCommand(source_command)

                # 格式不对
                if not command_dict:
                    return

                # 执行
                for _ in range(times):
                    executeCommand(img_path, command_dict, interval)

                # 运行到循环结束区间
                if i == part_cycle_end and part_cycle_time != 1:
                    # 仍需要循环执行，i指向循环起始区间
                    i = part_cycle_start
                    part_cycle_time -= 1
                    continue

                i += 1
        except Exception as e:
            myLog("第{}次循环出错：{}".format(cycle_time, str(e.args[0])))


if __name__ == '__main__':
    main()
    os.system("pause")
