import os
import sys
import shutil
import requests
from bs4 import BeautifulSoup
from PIL import Image
from threading import Thread
from urllib.parse import quote, unquote  # URL中文转义
import re
import hashlib
import time


# 本代码用于下载桌面浏览器能够打开的腾讯微信公众号网页中所包含的图像
# 2024年7月6日


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
}

STATIC = r"D:\Lab\dwebp.exe"
SAVE_DIRECTORY = r"D:\wc"


waiting = """


"""


URLS = [


]

def get_soup_from_webpage(url: str, header: str, timeout=None):
    attempts = 0
    success = False
    while attempts < 6 and not success:
        try:
            response = requests.get(url, headers=header, timeout=15)
            if response.status_code == requests.codes.ok:  # ok means 200 only

                content = response.text
                soup = BeautifulSoup(content, 'lxml')
                success = True
            else:
                print(f"{url} 下载失败 状态码： {response.status_code}")
                break
        except:
            print(f"{url} \t 连接错误，无法加载\n")
            # 以等差数列添加等待时间间隔
            print(
                f'尝试打开 {url} 时发生网络错误，等待{5*attempts + 5}秒钟后进行第{attempts + 1}次尝试')
            time.sleep(5*attempts + 5)
            attempts += 1

    return soup, content


def make_name_valid(validname):
    validname = validname.replace('\\', '_')
    validname = validname.replace('.', '_')
    validname = validname.replace('/', '_')
    validname = validname.replace(':', '_')
    validname = validname.replace('*', '_')
    validname = validname.replace('?', '_')
    validname = validname.replace('"', '_')
    validname = validname.replace('<', '_')
    validname = validname.replace('>', '_')
    validname = validname.replace('|', '_')
    validname = validname.replace('|', '_')
    validname = validname.replace('\t', '_')
    validname = validname.replace('\r', '_')
    validname = validname.replace('\n', '_')
    # \xa0 Unicode represents a hard space or a no-break space in a program.
    validname = validname.replace('\xa0', '')
    validname = validname.replace('～', '')
    validname = validname.strip()
    return validname


def extract_image_url(soup: BeautifulSoup) -> list:
    raw_down_list = []
    try:
        tags = soup.find_all('img')
        for n in tags:
            raw_down_list.append(n['data-src'])
    except:
        # 从 2023-03-03 开始，微信使坏，开始用JavaScript来对图片地址进行隐藏
        hidden_section = soup.find('div', id="js_content")
        hidden_img_tags = hidden_section.find_all('img')
        for n in hidden_img_tags:
            raw_down_list.append(n['data-src'])

    # 去重
    downlist = list(set(raw_down_list))
    return downlist


def extract_image_from_cdn_version_page(content: str) -> list:
    pattern = r"cdn_url:\s*'([^']*)'"

    raw_down_list = re.findall(pattern, content)
    cleaned_urls = [url.split("\\")[0] for url in raw_down_list]

    if raw_down_list:
        # 去重
        downlist = list(set(cleaned_urls))
        return downlist
    else:
        print("No image URLs found.")


def find_filename(img_url: str) -> str:
    if "wx_fmt=" in img_url:
        img_format = img_url.split("wx_fmt=")[-1]

        # 2024年4月24日，微信又使坏：
        # ct19v2f1gLoUVDMdY95YDiaLdgc8orQMH2M3ITZDPkKHK5Vxn4VqHtmw.jpeg&wxfrom=5&wx_lazy=1&wx_co=1
        if '&' in img_format:
            img_format = img_format.split("&")[0]

        # https://mmbiz.qpic.cn/sz_mmbiz_jpg/aiauu2lGXR28QkTDPwicxYaZ3vtzGCbHicibYsdtJmYMibhiaWfjZoAM7tpR9Ad6F2tcDuSg5tOQUuySiaw3ibCmdEF5xA/640?wx_fmt=other&from=appmsg&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp
        if img_format == 'other' and 'tp=webp' in img_url:
            img_format = "webp"

    # https://mmbiz.qpic.cn/mmbiz_jpg/2Gd6nk4y4a9HnbVElBXgSxa7XzL0ekkySkiczOUpauoVh1eVYaFibOySp1dhH6ZlGicsRQ5fXyHXM8ibpwoGIlfqIQ/640?from=appmsg
    elif "https://mmbiz.qpic.cn/mmbiz_jpg/" in img_url:
        img_format = ".jpg"
        filename = img_url.split("/")[-2][33:] + img_format
        return filename

    filename_without_format = img_url.split("/")[-2][33:]
    filename = filename_without_format + '.png'

    return filename


def find_title(url: str, soup: BeautifulSoup):
    try:
        web_title = soup.find(
            'h1', class_='rich_media_title').get_text().strip()

    except AttributeError:
        try:
            meta_web_title = soup.find("meta", property="og:title")
            web_title = meta_web_title['content']

        except TypeError:
            return "The content has been deleted by the author."

    return web_title


def rillaget(url: str, title: str, header: str) -> None:
    try:
        filename = find_filename(url)
        total_path = os.path.join(
            SAVE_DIRECTORY, make_name_valid(title), filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(total_path), exist_ok=True)

        response = requests.get(url, headers=header, stream=True, timeout=30)

        # Check if response is successful
        if response.status_code == 200:
            expected_length = int(response.headers.get('Content-Length', 0))
            current_length = 0

            with open(total_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    current_length += len(chunk)

                    # Content-Length check
                    if current_length >= expected_length:
                        break

            # Conver WebP to PNG
            if '.webp' in total_path:
                print(f"Found Webp! {repr(total_path)}")
                webp_to_png(repr(total_path))

            # Use md5 to rename the file
            rename_to_md5(total_path)

        else:
            print(f"Failed to download {url}. HTTP Status Code: {
                  response.status_code}")

    except Exception as e:
        print(f"Error occurred while downloading {url}:\n{str(e)}")


def webp_to_png(webp_filepath):
    save_path = webp_filepath.replace('webp', 'png')
    cmd = f'{STATIC} "{webp_filepath}" -o "{save_path}"'
    print(cmd)
    os.system(cmd)
    os.remove(webp_filepath)
    sys.exit()


def rename_to_md5(filepath):
    file_name = filepath.split("\\")[-1].split(".")[0]
    new_name = get_md5(filepath)
    new_path = filepath.replace(file_name, new_name)
    os.rename(filepath, new_path)


def get_md5(filepath):
    # Open,close, read file and calculate MD5 on its contents
    with open(filepath, 'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()
        # pipe contents of the file through
        md5_returned = hashlib.md5(data).hexdigest()

    # Finally compare original MD5 with freshly calculated
    return md5_returned


def normal():
    for index, url in enumerate(URLS, start=1):

        soup, content = get_soup_from_webpage(url, HEADER, 15)
        # soup, content = get_soup_from_localhtml('soup.html')

        # soup = BeautifulSoup(content, features='lxml')
        title = find_title(url, soup)
        if title == "The content has been deleted by the author.":
            print(f"{index} 来晚了，内容被和谐了。（；´д｀）ゞ {url}")
            continue

        print(index, title, url)

        downlist = extract_image_url(soup)
        if not downlist:
            print("cdn")
            downlist = extract_image_from_cdn_version_page(content)

        # downlist = set(downlist)

        # for link in downlist:
        #     print(link)
            # print(find_filename(link))

        # skip emoji
        for link in downlist[:]:
            if "/we-emoji/" in link:
                downlist.remove(link)
                continue

        print(f"共找到{len(downlist)}张图片")

        threads = []
        for img_url in downlist:
            t = Thread(target=rillaget, args=[img_url, title, HEADER])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        print()


if __name__ == '__main__':
    normal()

