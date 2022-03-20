import os
import requests
import time
from bs4 import BeautifulSoup
from threading import Thread


# 初代爬取Mobile01上照片原图的程式
# 2022年3月19日

# Fujifilm GFX50S II 評測報告｜6.5級 IBIS 超有感 規格齊備的中片幅之選！ - Mobile01

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 "
           "(KHTML, like Gecko) Version/15.0 Safari/605.1.15"}
SAVE_DIRECTORY = r'D:\Imperial Readings\My pictures\Mobile01\2020\2020 Mobile01'
SAVE_DIRECTORY_H = r'D:\Imperial Readings\My pictures\Mobile01\2020\2020 Mobile01'


def withdraw_data_src(content):
    for item in content:
        try:
            img_url_repeat = item.get('data-src')
        except:
            pass
    return img_url_repeat


def rillaget(url, dir_name, header):
    filename = url.split("/")[-1]
    total_path = os.path.join(dir_name, filename)

    try:
        response = requests.get(url, headers=header, timeout=50)

        if response.status_code == requests.codes.ok:  # ok means 200 only
            with open(total_path, 'wb') as fd:
                for chunk in response.iter_content(1024):
                    fd.write(chunk)
            print(f"{filename}  下载成功")
        else:
            print(f"{url} 下载失败 状态码： {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"{url} \t 无法加载\n")

    except Exception as e:
        print(f"{url} 发生异常：\n{e}")


def get_soup_from_localhtml(webpage):
    soup = BeautifulSoup(open(webpage, encoding='utf-8'), features='lxml')
    # 抛弃网页中的垃圾元素，加快处理速度
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()
    return soup


def extract_image_url(soup):
    '''从网页soup中提纯原图url'''
    h_downlist = []
    l_downlist = []
    r_downlist = []
    div_itemprop_articleBody = soup.find('div', itemprop="articleBody")

    # 高清部分
    tag_a = div_itemprop_articleBody.find_all('a')
    for content in tag_a:

        img_url_high_resolution = content.get('href')
        if img_url_high_resolution and 'https://attach.mobile01.com/attach/' in img_url_high_resolution:
            h_downlist.append(img_url_high_resolution)

        # 找到重复的非高清的图片
        for item in content:
            try:
                img_url_repeat = item.get('data-src')
                if img_url_repeat and 'https://attach.mobile01.com/attach/' in img_url_repeat:
                    r_downlist.append(img_url_repeat)
            except:
                pass

    # 非高清部分
    tag_img = div_itemprop_articleBody.find_all('img')
    for content in tag_img:
        img_url_low_resolution = content.get('data-src')
        if img_url_low_resolution and 'https://attach.mobile01.com/attach/' in img_url_low_resolution:
            l_downlist.append(img_url_low_resolution)

    # 剔除重复的非高清图片
    if len(r_downlist) < len(l_downlist):
        print(f"已经智能剔除重复的图片{len(l_downlist)-len(r_downlist)}张")
        real_l_list = [i for i in l_downlist if i not in r_downlist]
    else:
        return h_downlist, l_downlist

    return h_downlist, real_l_list


def bring_mm_home(downlist, directory):
    threads = []
    for url in downlist:
        t = Thread(target=rillaget, args=[url, directory, HEADERS])
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def play():
    soup = get_soup_from_localhtml("soup.html")
    title = soup.title.string

    h_list, l_list = extract_image_url(soup)

    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)

    if not os.path.exists(SAVE_DIRECTORY_H):
        os.makedirs(SAVE_DIRECTORY_H)

    bring_mm_home(h_list, SAVE_DIRECTORY_H)
    bring_mm_home(l_list, SAVE_DIRECTORY)

    print(title)

if __name__ == '__main__':

    play()

    print("～～完结撒花～～")
