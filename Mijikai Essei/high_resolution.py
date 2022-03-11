import os
from PIL import Image

SRC_FOLDER = 'D:\SRC'

DEST_FOLDER = 'D:\DEST'

# 遍历文件夹，筛选分辨率高的那一撮
# 把不达标的文件夹改名字——往前面加入low字段，以便排序选择。

paths = os.listdir(SRC_FOLDER)

def picture_selection(path):
    image_width_sum = []
    image_height_sum = []
    images = os.listdir(path)

    if images:
        number_to_be_divided = len(images)
    else:
        print("文件夹中没有图片")
        return

    for image in images:
        image_path = os.path.join(path, image)
        with Image.open(image_path) as picture:
            image_width, image_height = picture.size
            image_width_sum.append(image_width)
            image_height_sum.append(image_height)

    image_width_average = sum(image_width_sum)//number_to_be_divided
    image_height_average = sum(image_height_sum)//number_to_be_divided
    if image_width_average + image_height_average <= 2500:
        print(
            (f"本帖图片分辨率过低，只有 {image_width_average} × {image_height_average} ，跳过～～"))
        print(path)
        if "[亞洲]" in path:
            new_path = path.replace("[亞洲]", "low")
            os.rename(path, new_path)
        elif "[寫真]" in path:
            new_path = path.replace("[寫真]", "low")
            os.rename(path, new_path)

    else:
        print(
            f"本帖图片分辨率为 {image_width_average} × {image_height_average}")


for path in paths:
    print(path)
    path = os.path.join(SRC_FOLDER, path)
    try:
        picture_selection(path)
    except Exception:
        os.rename(path, path + 'Error')

    print()
