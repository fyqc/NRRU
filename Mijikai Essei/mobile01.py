import os
import shutil
import requests
from bs4 import BeautifulSoup
from threading import Thread
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


# yt-dlp -x --audio-format mp3 https://www.youtube.com/watch?v=6j0riQjd7Sc

# Mobile01 images downloader 3nd Version
# 8/20/2023

# Wotancraft 「New Pilot 飛行員」18L 相機後背包｜直覺快取 機能性依舊！
# 08-15
# 吉姆林


HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 "
           "(KHTML, like Gecko) Version/15.0 Safari/605.1.15"}
SAVE_DIRECTORY = r'G:\Mobile01\820'
LOW_DIRECTORY = r'G:\Mobile01\820\LOW'


def play():
    soup = get_soup_from_localhtml("soup.html")
    title = soup.title.string

    print(title)

    h_list, l_list, deleted_images_number_status_message = extract_image_url(
        soup)

    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)

    bring_mm_home((h_list + l_list), SAVE_DIRECTORY)

    put_low_resolution_aside()

    if deleted_images_number_status_message:
        print(deleted_images_number_status_message)
    recall_title(title)



def put_low_resolution_aside():
    images = os.listdir(SAVE_DIRECTORY)
    if images:
        for image in images:
            image_path = os.path.join(SAVE_DIRECTORY, image)
            with Image.open(image_path) as picture:
                image_width, image_height = picture.size
            if image_width < 800:
                if not os.path.exists(LOW_DIRECTORY):
                    os.makedirs(LOW_DIRECTORY)
                shutil.move(image_path, LOW_DIRECTORY)
    
    else:
        print("获取图片失败")


def recall_title(title):
    print("\n", title, "\n")

    # Sony FX30 評測報告
    if " 評測報告" in title:
        title = title.replace("評測報告", "")

    if " - Mobile01" in title:
        title = title.replace(" - Mobile01", "")

    # 「雙鏡評測」Canon RF24mm f/1.8 Macro & RF15-30mm f/4.5-6.3
    if "」" in title:
        title = title.split("」")[-1]

    reanme_draft = title.split("｜")[0].strip()
    print(reanme_draft)


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
                fd.write(response.content)
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
        if img_url_high_resolution:
            if 'https://attach.mobile01.com/attach/' in img_url_high_resolution:
                h_downlist.append(img_url_high_resolution)
            elif '//attach.mobile01.com/attach/' in img_url_high_resolution:
                h_downlist.append("".join(['https:', img_url_high_resolution]))

        # 找到重复的非高清的图片
        for item in content:
            try:
                img_url_repeat = item.get('data-src')
                if img_url_repeat:
                    if 'https://attach.mobile01.com/attach/' in img_url_repeat:
                        r_downlist.append(img_url_repeat)
                    elif '//attach.mobile01.com/attach/' in img_url_repeat:
                        r_downlist.append("".join(['https:', img_url_repeat]))
                else:
                    img_url_repeat = item.get('src')
                    if img_url_repeat:
                        if 'https://attach.mobile01.com/attach/' in img_url_repeat:
                            r_downlist.append(img_url_repeat)
                        elif '//attach.mobile01.com/attach/' in img_url_repeat:
                            r_downlist.append(
                                "".join(['https:', img_url_repeat]))
            except:
                pass

    # 非高清部分
    tag_img = div_itemprop_articleBody.find_all('img')
    for content in tag_img:

        img_url_low_resolution = content.get('data-src')
        if img_url_low_resolution:
            if 'https://attach.mobile01.com/attach/' in img_url_low_resolution:
                l_downlist.append(img_url_low_resolution)
            elif '//attach.mobile01.com/attach/' in img_url_low_resolution:
                l_downlist.append("".join(['https:', img_url_low_resolution]))
        else:
            img_url_low_resolution = content.get('src')
            if img_url_low_resolution:
                if 'https://attach.mobile01.com/attach/' in img_url_low_resolution:
                    l_downlist.append(img_url_low_resolution)
                elif '//attach.mobile01.com/attach/' in img_url_low_resolution:
                    l_downlist.append(
                        "".join(['https:', img_url_low_resolution]))

    # 剔除重复的非高清图片
    if len(r_downlist) < len(l_downlist):
        deleted_images_number_status_message = f"已经智能剔除重复的图片{len(l_downlist)-len(r_downlist)}张"
        real_l_list = [i for i in l_downlist if i not in r_downlist]
    else:
        return h_downlist, l_downlist

    return h_downlist, real_l_list, deleted_images_number_status_message


def bring_mm_home(downlist, directory):
    threads = []
    for url in downlist:
        t = Thread(target=rillaget, args=[url, directory, HEADERS])
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == '__main__':
    play()
    print("～～完结撒花～～")
