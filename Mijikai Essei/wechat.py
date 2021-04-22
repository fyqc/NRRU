from bs4 import BeautifulSoup
import requests
import time

# 现在时间：2021年4月22日14时10分15秒
# 本代码用于下载桌面浏览器能够打开的腾讯微信公众号网页中所包含的图像

print('https://mp.weixin.qq.com/s/KAI2s49-pXLtPX7FudnRQg')
url = input('输入要下载的微信公众号的网址，格式如上： ')

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

response = requests.get(url, headers=header)
content = response.text
soup = BeautifulSoup(content, 'lxml')

# tag_title = soup.find_all('h2', class_='rich_media_title')[0].get_text().strip() # 用find_all拿到的是个列表，需要切片
tag_title = soup.find('h2', class_='rich_media_title').get_text().strip() # 因为该class近出现一次，所以就不切片，直接用find就好

# strip()去除字符串首位空格
'''
                <h2 class="rich_media_title" id="activity-name">
                    
                    
                    
30款衣裙报告！天南海北云逛街+日常
                </h2>
'''

# 打印公众号文章的网页标题
print(tag_title)

# 分析图片url
# <div class="rich_media_content " id="js_content" style="visibility: hidden;">
tag_div = soup.find_all('div', class_='rich_media_content')
div_bf = BeautifulSoup(str(tag_div), 'lxml')
tag_img = div_bf.find_all('img')

# <section style="max-width: 100%;vertical-align: middle;display: inline-block;line-height: 0;width: 90%;box-sizing: border-box;"><img data-ratio="1.371179" data-w="687" data-src="https://mmbiz.qpic.cn/mmbiz_png/PiblzyR5tICS6thcXkLgfC399Cwa3dkC0t3wyw4Q0icwffJ66NMtAuqqv9BeSWxRflMNHriaOtIokVXyFFCRTVdnw/640?wx_fmt=png" style="vertical-align: middle;max-width: 100%;width: 100%;box-sizing: border-box;" width="100%" data-type="png"  />
for x in tag_img:
    img_raw_url = x.get('data-src')
    # https://mmbiz.qpic.cn/mmbiz_png/PiblzyR5tICS6thcXkLgfC399Cwa3dkC0t3wyw4Q0icwffJ66NMtAuqqv9BeSWxRflMNHriaOtIokVXyFFCRTVdnw/640?wx_fmt=png
    filename_no_tail = img_raw_url.split("/")[-2]
    # PiblzyR5tICS6thcXkLgfC399Cwa3dkC0t3wyw4Q0icwffJ66NMtAuqqv9BeSWxRflMNHriaOtIokVXyFFCRTVdnw
    filename = filename_no_tail[33:]
    # t3wyw4Q0icwffJ66NMtAuqqv9BeSWxRflMNHriaOtIokVXyFFCRTVdnw
    img_url = img_raw_url

    webdata = requests.get(img_url, headers=header, timeout=30)

    total_path = r'D:\RMT\TRY\Wechat' + '/' + filename + '.jpg' # 加上.jpg很重要

    if 'Content-Length' in webdata.headers and len(webdata.content) == int(webdata.headers['Content-Length']):
        with open(total_path, 'wb') as f:
            for chunk in webdata.iter_content(1024):
                f.write(chunk)
            f.close()
        print(filename + "下载成功")
