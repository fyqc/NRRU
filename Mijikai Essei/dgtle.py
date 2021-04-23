import os 
import time
import requests
from bs4 import BeautifulSoup
from threading import Thread

'''
把需要下载的快捷方式统一放在DGT文件夹中
运行该文件即可
'''


# 现在时间：2021年4月23日02时07分35秒
# ～～～～从头推倒重写一遍咯～～～～
# 发现会把不是本篇文章里的图片也加载进来，需要在Soup中加以限定。
# 明天在搞了


# GET WEBPAGE URL FROM SHORTCUT LINKAGES IN CERTAIN FOLDER
def internet_shortcut(rootdir):
    webpage_list = []
    for (_,_,filenames) in os.walk(rootdir):
        for filename in filenames:
            if filename.endswith('.URL'):
                with open(rootdir + '/'+ filename, "r", encoding='utf-8') as f:
                    webpage = f.read().split('\n')[1][4:]
                    # 加一道保险，100％确定拿到的是url地址
                    if webpage.startswith('http'):
                        webpage_list.append(webpage)
    return webpage_list

# USE BEAUTIFULSOUP TO PARSING HTML AND XML DOCUMENTS
def get_soup_from_webpage(url, header):
    response = requests.get(url, headers=header)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_soup_from_localhtml(webpage):
    soup = BeautifulSoup(open(webpage, encoding='utf-8'), features='lxml')
    return soup

# FIND TITLE USING BS4
def find_title(soup):
    web_title = soup.title.get_text()
    return web_title

# FIND AUTHOR AND USE IT AS FOLDER'S NAME
def find_author(soup):
    # This is for Inst page, and if it is not, which will return None
    if soup.find('div', class_='interset-content-top'): 
        # In that case, skip this line, goto next condition
        author = soup.find('div', class_='interset-content-top').get_text().strip().split("\n")[0] 
    else: # Choose Article page instead.
        author = soup.find('span', class_='author').get_text()
    return author

# EXTRACT IMAGE URL USING BS4
def extract_image_url(soup):
    downlist = []
    tags = soup.find_all('img')
    for n in tags:

        # Article Type
        if n.get('data-original'):
            raw_img_url = n.get('data-original')
        # Inst Type and majority of Article Type
        elif n['src']:
            raw_img_url = n.get('src')
        # 修剪杂枝
        img_url = raw_img_url.replace('_1800_500','').split("?")[0]

        if 'dgtle_img/article' in img_url or 'dgtle_img/ins' in img_url:
            downlist.append(img_url)
    
    if len(downlist) == 0:
        print("什么也没找到，他们可能又双叒叕改版了。咱们也升级代码吧。")
    
    # 去重
    downlist = list(set(downlist))
    return downlist

# DUE TO THE POOR SERVER CONNECTION, IT IS NECESSARY TO KEEP TRYING MULTIPLE TIMES
def try_soup_ten_times(url, header):
    soup_attemp = 0
    success_status = False
    while soup_attemp < 10 and not success_status:
        try:
            soup = get_soup_from_webpage(url, header) # 实际用
            # soup = get_soup_from_localhtml('arti.html') # 测试用
            title = find_title(soup)
            print(title)
            dir_name = find_author(soup)
            downlist = extract_image_url(soup)
            print(f'Author is: {dir_name}')
            print(f'找到 {len(downlist)} 张图片')
            success_status = True
        except:
            soup_attemp += 1
            print("链接有点不通畅啊……")
            print("等五秒试试")
            time.sleep(5)
            print("继续……")
            if soup_attemp == 10:
                print("算了，放弃吧。")
                break
    return dir_name, downlist

# THE CORE OF THIS CODE IS DOWNLOAD IMAGE W/O ANY ISSUES.
def rillaget(url, dir_name, header):
    # 这一版和旧版最大的不同是把下载器做了拆分，不再负责分解downlist
    # 只执行单个的url，这样做的目的是为了进行多线程加速
    if not os.path.exists(dir_name): 
        os.mkdir(dir_name)
    filename = url.split("/")[-1]
    attempts = 0
    success = False
    while attempts < 5 and not success:
        try:
            total_path = dir_name + '/' + filename
            response = requests.get(url, headers=header, timeout=30)
            if 'Content-Length' in response.headers and len(response.content) == int(response.headers['Content-Length']):
                with open(total_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                    f.close()
                print(filename + "  下载成功")
                success = True
            else:
                print("图片可能不完整，重来一次。")
        except:
            print(filename + '正在重新下载')
            attempts += 1
            if attempts == 5:
                break

if __name__ == '__main__':
    rootdir=r'D:\RMT\DGT'
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}
    webpage_list = internet_shortcut(rootdir)
    for URL in webpage_list:
        dir_name, downlist = try_soup_ten_times(URL, header)
        threads = []
        for url in downlist:
            t = Thread(target = rillaget, args = [url, dir_name, header])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
