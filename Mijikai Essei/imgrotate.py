from PIL import Image, ExifTags
import os

# 根据照片的Exif信息里面定义的方向旋转jpg图片
# 发现旋转后的图片体积会极大的减小，虽然肉眼看不出画质差异，但是心理上并不能接受，这是一个半成品

cat=[]
dirpath = r'D:\RMT\rotimg'
for file in os.listdir(dirpath):
    if os.path.isfile(os.path.join(dirpath, file)) == True:
        c= os.path.basename(file)
        name = dirpath + '\\' + c
        cat.append(name)

for filepath in cat:
    try:
        image=Image.open(filepath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(image._getexif().items())

        if exif[orientation] == 3:
            image=image.transpose(Image.ROTATE_180)
        elif exif[orientation] == 6:
            image=image.transpose(Image.ROTATE_270)
        elif exif[orientation] == 8:
            image=image.transpose(Image.ROTATE_90)
        image.save(filepath)
        image.close()

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

