import os
from PIL import Image, ImageSequence

# 2023年9月10日
# 用于将webp格式文档自动判断其是否为动图，转为png或gif

STATIC = r"F:\Lab\libwebp-1.3.1-windows-x64\bin\dwebp.exe"  # Google
ANIMATION = r"F:\Lab\giffix\FbWebp2Gif\FbWebp2Gif.exe"  # Github
DIRECTORY = r"F:\Lab\giffix\Wait"

def is_animation(file):
    image = Image.open(file)
    count = 0
    for frame in ImageSequence.Iterator(image):
        count += 1
    return count > 1


os.chdir(DIRECTORY)
files = os.listdir(DIRECTORY)

for file in files:
    if ".webp" in file:
        if is_animation(file):
            source = os.path.join(DIRECTORY, file)
            cmd = f"{ANIMATION} {source}"
            print(cmd)
            os.system(cmd)
            print()

        else:
            source = os.path.join(DIRECTORY, file)
            destination = os.path.join(DIRECTORY, file.replace('webp', 'png'))
            cmd = f'{STATIC} "{source}" -o "{destination}"'
            print(cmd)
            os.system(cmd)
            print()
