import os
import time
import requests
from bs4 import BeautifulSoup
from threading import Thread

'''
把需要下载的快捷方式统一放在DGT文件夹中
运行该文件即可
'''


# 2023年11月6日
# https://www.dgtle.com/inst-1893720-1.html
# 发现以上帖子访问时出错，正文提示：
# 无法找到内容
# 内容已删除或正在审核，稍候再看吧~


def internet_shortcut(rootdir = os.getcwd()):
    '''
    GET WEBPAGE URL FROM SHORTCUT LINKAGES IN CERTAIN FOLDER.
    '''
    webpage_list = []
    for (_, _, filenames) in os.walk(rootdir):
        for filename in filenames:
            if filename.lower().endswith('.url'):
                with open(rootdir + '/' + filename, "r", encoding='utf-8') as f:
                    webpage = f.read().split('\n')[1][4:]
                    # Just be sure the data we acquired is URL
                    if webpage.startswith('http'):
                        webpage_list.append(webpage)
    return webpage_list

def get_soup_from_webpage(url, header):
    '''
    USE BEAUTIFULSOUP TO PARSING HTML AND XML DOCUMENTS.
    '''
    response = requests.get(url, headers=header)
    # The encoding here shall be modified as per the web source.
    response.encoding = 'utf-8'
    return BeautifulSoup(response.text, 'lxml')


def get_soup_from_localhtml(webpage):
    soup = BeautifulSoup(open(webpage, encoding='utf-8'), features='lxml')
    return soup


# FIND TITLE USING BS4
def find_title(soup):
    return soup.title.get_text()


def find_author(soup):
    '''
    FIND AUTHOR AND USE IT AS FOLDER'S NAME.
    '''
    # This is for Inst page, and if it is not, which will return None
    if soup.find('div', class_='interset-content-top'):
        # In that case, skip this line, goto next condition
        author = soup.find(
            'div', class_='interset-content-top').get_text().strip().split("\n")[0]
    else:  # Choose Article page instead.
        author = soup.find('span', class_='author').get_text()
    return author


def extract_image_url(soup):
    '''
    EXTRACT IMAGE URL USING BS4.
    '''
    downlist = []
    # 一些Article的文章下方会有评论区，会附带上作者的其它文章里面的图，甚至可能会有留言者附加的图片
    # 这里的四行代码用于把整个评论区包括“XXXX的更多文章”去掉
    # 用try……except……结构是为了防止在没有该部分的时候报错
    try:
        soup.find('div', class_="comment-hot-new-warp").decompose()
    except:
        pass

    tags = soup.find_all('img')
    for n in tags:
        # Article Type
        if n.get('data-original'):
            raw_img_url = n.get('data-original')
        # Inst Type and majority of Article Type
        elif n['src']:
            raw_img_url = n.get('src')
        # 修剪杂枝
        # 2021年7月15日出现一种新格式的图片，没有后缀，实际为jpg
        # http://s1.dgtle.com/dgtle_img/article/2021/07/15/74e7f202107151213512077_1800_500_w
        img_url = raw_img_url.replace('_1800_500_w.', '.').split("?")[0]
        img_url = img_url.replace('_1800_500.', '.').split("?")[0]
        if 'dgtle_img/article' in img_url or 'dgtle_img/ins' in img_url:
            downlist.append(img_url)

    if len(downlist) == 0:
        print("什么也没找到，他们可能又双叒叕改版了。咱们也升级代码吧。")

    # 去重
    downlist = list(set(downlist))
    return downlist


def try_soup_ten_times(url, header):
    '''
    DUE TO THE POOR SERVER CONNECTION, IT IS NECESSARY TO KEEP TRYING MULTIPLE TIMES.
    '''
    soup_attemp = 0
    success_status = False
    while soup_attemp < 10 and not success_status:
        try:
            soup = get_soup_from_webpage(url, header)  # 实际用
            # soup = get_soup_from_localhtml('arti.html') # 测试用
            title = find_title(soup)
            print(title)
            if title == " 数字尾巴 分享美好数字生活":
                print("帖子大概被和谐了")
            if "无法找到内容" in soup.get_text() or "内容已删除或正在审核" in soup.get_text():
                print("惋惜，下一个！")
                return ("404","404")
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
                return ("404","404")
    return dir_name, downlist


def make_folder_asper_author(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def rillaget(link, dir_name, header):
    '''
    THE CORE OF THIS CODE IS DOWNLOAD IMAGE W/O ANY ISSUES.
    '''
    filename = link.split("/")[-1]
    if filename[-11:] == "_1800_500_w":
        filename = "".join([filename, '.jpg'])
    total_path = dir_name + '/' + filename
    attempts = 0
    success = False
    while attempts < 8 and not success:
        try:
            response = requests.get(link, headers=header, timeout=5)
            
            if len(response.content) == int(response.headers['Content-Length']):
                with open(total_path, 'wb') as fd:
                    for chunk in response.iter_content(1024):
                        fd.write(chunk)
                print(filename + "  下载成功")
                success = True
        except:
            # 以等差数列添加等待时间间隔
            print(f'尝试下载 {filename} 时发生网络错误，等待{5*attempts + 5}秒钟后进行第{attempts + 1}次尝试')
            time.sleep(5*attempts + 5)
            attempts += 1
    if attempts == 8:
        print(f"{filename} 下载失败")


if __name__ == '__main__':
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

# 测试时把以下部分注释掉
    webpage_list = internet_shortcut()
    for weblink in webpage_list:
        dir_name, downlist = try_soup_ten_times(weblink, header)
        if downlist == "404":
            continue
        make_folder_asper_author(dir_name)
        threads = []
        for link in downlist:
            t = Thread(target=rillaget, args=[link, dir_name, header])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()


# 测试解析图片格式时使用
    # soup = get_soup_from_localhtml('inst.html')
    # downlist = extract_image_url(soup)
    # print(downlist)
    # print(len(downlist))

# 以下是排故代码
    # URL = 'https://www.dgtle.com/inst-1893720-1.html'
