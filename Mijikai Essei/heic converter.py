import sys
import logging
import os
from multiprocessing import Pool
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

# 2026年1月11日

"""
用于把HEIC图片转换为PNG，可单独亦可批量
"""

# 直接拖放即可
# heic.bat
"""
@echo off
setlocal

:: 将所有拖拽的文件路径一次性传给 Python 脚本
py D:/Rilla/"heic converter.py" %*

echo 处理完成！
pause
"""

# 注册解码器，使 Pillow 能够识别 .heic 文件
register_heif_opener()

LOG_FILEPATH = r'D:\Rilla\Log\heic.log'


def setup_logging():
    log_dir = os.path.dirname(LOG_FILEPATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler(filename=LOG_FILEPATH,
                                mode="a", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def convert_one(heic_filepath):
    """单张图片处理函数，放入子进程"""
    # 必须在子进程中重新注册，否则会报错找不到解码器
    register_heif_opener()

    base, ext = os.path.splitext(heic_filepath)
    if ext.lower() != '.heic':
        return f"跳过非HEIC: {heic_filepath}"

    png_filepath = base + ".png"
    try:
        with Image.open(heic_filepath) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # 优化速度：设置 PNG 压缩级别为较快
            img.save(png_filepath, format="PNG", compress_level=1)

        os.remove(heic_filepath)
        return f"成功: {heic_filepath}"
    except Exception as e:
        return f"失败: {heic_filepath}, 错误: {str(e)}"


if __name__ == '__main__':
    setup_logging()

    # 获取拖拽过来的所有文件列表
    # sys.argv[0] 是脚本路径，sys.argv[1:] 是所有拖入的文件
    input_files = [f.strip('"') for f in sys.argv[1:]]

    if not input_files:
        print("未检测到文件！")
        sys.exit(1)

    logging.info(f"收到 {len(input_files)} 个任务，准备开始...")

    # 如果只有一张图，直接跑，没必要开进程池
    if len(input_files) == 1:
        result = convert_one(input_files[0])
        logging.info(result)
    else:
        # 多进程处理批量图片
        # 即使拖入 100 张，Python 也只启动一次，极大地减少了开销
        with Pool() as pool:
            results = pool.map(convert_one, input_files)
            for res in results:
                logging.info(res)
