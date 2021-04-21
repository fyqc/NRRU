# 验证图片完整性

import io
import imghdr
from os import PathLike 
from PIL import Image

def IsValidImage(file): 
    bValid = True
    if isinstance(file, (str, PathLike)):
        fileObj = open(file, 'rb')
    else:
        fileObj = file
    
    buf = fileObj.read()
    if buf[6:10] in (b'JFIF', b'Exif'):     #jpg图片
        if not buf.rstrip(b'\0\r\n').endswith(b'\xff\xd9'):
            bValid = False
    else:        
        try:  
            Image.open(fileObj).verify() 
        except:  
            bValid = False
         
    return bValid

print(IsValidImage(r'D:\Eiderdown\134021vdeofhqjh9ddikde.jpg'))
