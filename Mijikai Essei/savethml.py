# coding=utf-8


'''
打开url，将html保存到本地
'''

'''方法一'''
# import urllib.request


# url = 'https://www.vmgirls.com/12985.html'
# local = 'vmg.html'
# urllib.request.urlretrieve(url, local)

'''方法二'''
import requests

header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
url = 'https://www.vmgirls.com/9384.html'
# local = 'vmg.html'
html = requests.get(url, headers=header)
# print(html.text)
with open('9384.html','w',encoding='utf-8') as f:  
    f.write(html.text) 
