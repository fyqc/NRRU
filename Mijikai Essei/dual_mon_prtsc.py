import os

import win32api
from PIL import ImageGrab

# 2026年2月7日
# 用于在双显示器中对某一个显示器上的画面进行全屏截图操作


def capture_monitor(monitor_index=0):
    # 获取所有显示器的信息
    monitors = win32api.EnumDisplayMonitors()

    if monitor_index >= len(monitors):
        print(f"错误：找不到显示器 {monitor_index}")
        return

    # 获取指定显示器的坐标范围 (left, top, right, bottom)
    # monitors[monitor_index][2] 返回的就是该显示器的矩形区域坐标
    monitor_info = monitors[monitor_index][2]

    print(f"正在截取显示器 {monitor_index}，坐标范围: {monitor_info}")

    # ImageGrab.grab() 接受一个 bbox 参数 (left, top, right, bottom)
    # 这会直接按物理像素抓取，不会出现 Snipping Tool 那种 1 像素误差
    screenshot = ImageGrab.grab(bbox=monitor_info, all_screens=True)

    # 保存结果
    filename = f"monitor_{monitor_index}_cap.png"
    screenshot.save(filename)
    print(f"保存成功：{filename}，尺寸: {screenshot.size}")


def is_valid_filename(filename):
    try:
        with open(filename, "w") as f:
            pass
        os.remove(filename)
        return True
    except OSError:
        return False


# 测试

if __name__ == "__main__":
    # 0 通常是主显示器，1 是第二个显示器
    capture_monitor(0)
    pass
