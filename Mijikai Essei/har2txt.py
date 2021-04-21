import json # 引入json模块
import os # 引入os模块
'''
2:14 PM
12/19/2020

本代码将har文件内容转换成txt格式保存
'''

with open('vm.har', 'r', encoding='utf-8') as readObj: # 以“读”模式，打开同目录下的har文件，编码为“UTF-8”
        harDirct = json.loads(readObj.read()) # 使用json模块来读取里面的内容
        requestList = harDirct['log']['entries'] # 通过浏览153.har，获得里面的结构
            
        for item in requestList:
            urlString = (item['request']['url']) # 继续定位图片URL所在的位置
            print(urlString, file=open("load.txt", "a")) # 把生成的链接通过循环，打印成txt文本

