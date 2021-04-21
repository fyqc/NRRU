'''
https://www.jooies.cn/101#
社交媒体多种多样，不同的社交媒体有其具体的限制。
在图片张数方面，微博(weibo.com)和微信朋友圈限制每篇推文最多上传9张图片，
推特(twitter.com)更是过分，一条推文最多只能上传4张图片。
因此，在日常社交媒体的使用中，许多同学都会通过多张图片的拼接生成长图，
来达到发布更多图片的效果。网上有很多使用各种软件、库来拼接长图的手段，
但如果将社交媒体作为一种图片存储方式，原本拼接的长图，
如何重新分割成单独的图片，是一个比较复杂的问题。
'''

# 创建一个空的py文件，引入opencv库
from cv2 import cv2 

# cv2 读取需要分割的文件，获取图片的宽、高，并转成灰度图
# 使用RGB图也可以，转成灰度图的效率更高，准确度可能受到一定影响）
filename = "xlarge_VWb1_7292000000251e84.jpg"
image = cv2.imread(filename)
info = image.shape
height = info[0]
width = info[1]
gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)

# 从第二行开始，读取每一行的像素，与上一行的像素进行比较，
# 最终算出差异较大的像素数，记录差异较大的（本文差值25以上的将被记录，
# 具体数值可以多次尝试），如果有50%（可修改）以上不同的，即算作一条分割线，
# 最后用imshow画出分割线手动检查。建议将其定义为函数，提供一个确认是否完成的方式，
# 若并不精确，可以通过递归、重新定义精度，再做检查，最终完成
row = 1
marks = [] # mark the row we need
while row < height:
    column = 0
    all_num = 0
    while column < width:
        if abs(int(gray_image[row,column]) - int(gray_image[row-1,column])) > 25:
            all_num += 1
        column += 1
    if all_num/width*100 > 50:
        marks.append(row)
    row += 1
showimage = image.copy()
for mark in marks:
    cv2.line(showimage,(0,mark),(width,mark),(0,255,0),5)
cv2.namedWindow('split')
cv2.imshow('split', showimage)
cv2.waitKey(0)
marks.append(height)

# 通过记录下来的行号，最终分割图片，这里高度<10将被视为分割线，过滤掉
for inx, mark in enumerate(marks):
    if inx == 0:
        height_start = 0
    else:
        height_start = marks[inx - 1]
    height_end = mark
    if height_end - height_start > 10:
        output = image[height_start:height_end, 0:width]
        cv2.imwrite(filename[:-4] + '_' + str(inx) + filename[-4:], output)
