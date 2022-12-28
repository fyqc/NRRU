import os
import shutil
from PIL import Image

# 用于挑出符合特定分辨率的图片，并移动到指定文件夹中

DIRECTORY = r"F:\Reorgnize"
TARGET = r"F:\Reorgnize\BIG"

# 检测分辨率
def resolution(image_path):
    try:
        with Image.open(image_path) as picture:
            image_width, image_height = picture.size
    except Exception as e:
        print(f"发生异常：\n{e}")

    if image_width + image_height >= 2500:
        print(
            f"{image_path} 图片分辨率有 {image_width} × {image_height} ")
        SOURCE = os.path.join(DIRECTORY, image_path)
        shutil.move(SOURCE, TARGET)

# 遍历文件夹，获取文件
os.chdir(DIRECTORY)
files = os.listdir()
for file in files:
    resolution(file)
