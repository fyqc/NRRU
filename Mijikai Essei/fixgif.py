import os

# 用于修复损坏了的gif文件，以便可以在Windows 7的ACDSee 3.2上播放

DIRECTORY = r"D:\RMT\TRY\Review"
TARGET = r"F:\Lab\giffix"


files = os.listdir(DIRECTORY)
print(files)

for file in files:
    source = os.path.join(DIRECTORY, file)
    destination = os.path.join(TARGET, file)
    cmd = f'ffmpeg -i "{source}" "{destination}"'
    print(cmd)
    os.system(cmd)
    print()
