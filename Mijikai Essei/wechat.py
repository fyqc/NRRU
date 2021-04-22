# 本代码用于下载桌面浏览器能够打开的腾讯微信公众号网页中所包含的图像
# 新开发版本
# 现在时间：2021年4月22日17时30分43秒

from bs4 import BeautifulSoup
import requests
import os
from threading import Thread


def get_soup_from_webpage(url, header):
    response = requests.get(url, headers=header)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    return soup


def get_soup_from_localhtml(webpage):
    soup = BeautifulSoup(open(webpage, encoding='utf-8'), features='lxml')
    return soup


def extract_image_url(soup):
    raw_down_list = []
    tags = soup.find_all('img')
    for n in tags:
        try:
            # print(n['data-src'])
            raw_down_list.append(n['data-src'])
        except:
            # print('Nothing here')
            pass
    # 去重
    downlist = list(set(raw_down_list))
    return downlist


def find_filename(img_url):
    img_format = img_url.split("wx_fmt=")[-1]
    # filename_no_tail = img_raw_url.split("/")[-2]
    # filename = filename_no_tail[33:]
    filename_without_format = img_url.split("/")[-2][33:]
    filename = filename_without_format + '.' + img_format
    return filename


def find_title(soup):
    web_title = soup.find('h2', class_='rich_media_title').get_text().strip()
    return web_title

def input_url():
    print('https://mp.weixin.qq.com/s/KAI2s49-pXLtPX7FudnRQg')
    url = input('输入要下载的微信公众号的网址，格式如上： ')
    return url

def rillaget(url, header):
    filename = find_filename(url)
    total_path = r'D:\RMT\TRY\Wechat' + '/' + filename
    response = requests.get(url, headers=header, timeout=30)
    if 'Content-Length' in response.headers and len(response.content) == int(response.headers['Content-Length']):
        with open(total_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
            f.close()
        print(filename + "下载成功")


def rillatest(url):
    filename = find_filename(url)
    print(filename)


if __name__ == '__main__':
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}
    # url = input_url()
    # soup = get_soup_from_webpage(url, header)
# 测试用
    soup = get_soup_from_localhtml('wx.html')
    print(f"{find_title(soup)}")
    downlist = extract_image_url(soup)
    print(f"共找到{len(downlist)}张图片")
    threads = []
    for img_url in downlist:
        print(f"第 {int(downlist.index(img_url)) + 1} 张： ", end='')
        t = Thread(target = rillaget, args = [img_url, header])
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
        
        # rillaget(img_url, header)
# 测试用
        # rillatest(img_url)
