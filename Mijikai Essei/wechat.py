import hashlib
import os
import shutil
import subprocess
import re
import requests
import time
from bs4 import BeautifulSoup
from PIL import Image
from threading import Thread
from urllib.parse import quote, unquote


# 本代码用于下载桌面浏览器能够打开的腾讯微信公众号网页中所包含的图像
# 2024年7月25日


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


def make_name_valid(validname: str) -> str:
    validname = validname.replace('\\', '_')
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
    # 在 Windows 系统中建立文件夹时名字的最后不能是“．”，不论你加多少个点，都会被 Windows 忽略。
    validname = validname.rstrip(".")
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
        return None


def find_filename(img_url: str) -> str:
    # Rewrite this function, move 'image format decision' to downloader
    if 'mmbiz.qpic.cn' in img_url:
        return img_url.split("/")[-2]


def find_title(url: str, soup: BeautifulSoup) -> str:
    try:
        web_title = soup.find(
            'h1', class_='rich_media_title').get_text().strip()

    except AttributeError:
        try:
            meta_web_title = soup.find("meta", property="og:title")
            web_title = meta_web_title['content']

        except TypeError:
            try:
                web_title = soup.find(
                    'div', class_='weui-msg__title warn').get_text().strip()
            except Exception as e:
                print(e)

    return web_title


def rillaget(url: str, folder_path: str, header: str) -> None:
    try:
        response = requests.get(url, headers=header, stream=True, timeout=30)

        # Check if response is successful
        if response.status_code == 200:

            # Figure out image real format
            content_type_name = response.headers.get('Content-Type')
            image_format = content_type_name.split('/')[-1]

            filename = ".".join([find_filename(url), image_format])
            total_path = os.path.join(
                SAVE_DIRECTORY, folder_path, filename)

            # Skip existing file
            if os.path.exists(total_path):
                print(f"file already exists: {total_path}")
                return

            expected_length = int(response.headers.get('Content-Length', 0))
            current_length = 0

            with open(total_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    current_length += len(chunk)

                    # Content-Length check
                    if current_length >= expected_length:
                        break

            # Use md5 to rename the file
            rename_to_md5(total_path)

        else:
            print(
                f"Failed to download {url}. HTTP Status Code: {response.status_code}")

    except OSError as f:
        # "Cannot create a file when that file already exists"
        print(f)

    except Exception as e:
        print(f"Error occurred while downloading {url}:\n{str(e)}")


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


def webp_to_png(folder_path):
    for file in os.listdir(folder_path):
        if ".webp" in file:
            webp_path = os.path.join(folder_path, file)
            print(f"Found Webp! {webp_path}")
            png_path = webp_path.replace('webp', 'png')
            cmd = f'{STATIC} "{webp_path}" -o "{png_path}"'
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print("Error occurred:", result.stderr.decode())
            else:
                os.remove(webp_path)
                

def normal():
    for index, url in enumerate(URLS, start=1):

        soup, content = get_soup_from_webpage(url, HEADER, 15)
        # soup, content = get_soup_from_localhtml('soup.html')

        title = find_title(url, soup)
        if title == "The content has been deleted by the author." or title == "该内容已被发布者删除":
            print(f"  {index} 来晚了，内容被和谐了。（；´д｀）ゞ  ".center(78, "#"))
            print(title)
            print(url)
            print()
            continue

        print(index, title, url)

        downlist = extract_image_url(soup)
        if not downlist:
            print("cdn")
            downlist = extract_image_from_cdn_version_page(content)

        # skip emoji
        for link in downlist[:]:
            if "/we-emoji/" in link:
                downlist.remove(link)
                continue

        # Only if downlist is not empty
        if not len(downlist):
            print("没有发现图片，建议排故")
            print()
            break

        # Check if folder is there, if not, create one
        folder_path = os.path.join(
            SAVE_DIRECTORY, make_name_valid(title))

        # Ensure directory exists
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        print(f"共找到{len(downlist)}张图片")

        threads = []
        for img_url in downlist:
            t = Thread(target=rillaget, args=[img_url, folder_path, HEADER])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        # Check and convert WebP to PNG
        webp_to_png(folder_path)
        print()


if __name__ == '__main__':
    normal()

