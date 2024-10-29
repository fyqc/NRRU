import hashlib
import logging
import os
import shutil
import subprocess
import re
import requests
import time
from bs4 import BeautifulSoup
from PIL import Image
from threading import Thread

"""
用于微信公众号中的诸多图片保存

以文章标题为文件夹的名字
以图片本身的MD5作为文件名

将WebP自动转换为PNG

操作说明：
把URL复制进来，放在列表中
然后执行，就可以在目标文件夹中生成以标题为文件夹名的文件夹，里面是帖子中的图片
"""

# 2024年10月29日

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    # level=logging.DEBUG,
    level=logging.INFO,
    handlers=[logging.FileHandler(filename='tencent.log',mode='w',encoding='utf-8')]
)

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
}

STATIC = r"D:\Lab\dwebp.exe"  # 用于转换Webp格式为PNG
SAVE_DIRECTORY = r"D:\wc"

# 针对性修改此处
URLS = [

"https://mp.weixin.qq.com/s/C4BTn_YOcn8A7ANQq6Xw2A",

"https://mp.weixin.qq.com/s/ZK2-BaoiDluQphSJRvKWmw",

"https://mp.weixin.qq.com/s/wrg_qVA7LLNdO26cq8pP8g",

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
                logging.error(f"{url} 下载失败 状态码： {response.status_code}")
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


def extract_image_using_re_only(content: str) -> list:
    # cdn_url: 'https://mmbiz.qpic.cn/mmbiz_jpg/AicOhKNCfiaD9SHrapreD260eWviaANiaB100VoiasAeZicAo7Hl0qVTwKfzAUWB5Su4zhuQrtWK4OCwcgCnibUUbaL1g/0?wx_fmt=jpeg',
    # 'cdn_url':'https://mmbiz.qpic.cn/sz_mmbiz_gif/r7UskC2NBNCgceEu9iazYtvRMKezh8uAgScic6l4aM2BWwwcibmh50ofnI5uiaGAKRwDvXvWZYAS9VZdLttNhGDIxQ/640?wx_fmt=gif\x26amp;amp;from=appmsg'
    
    pattern = r"(?:['\"]?cdn_url['\"]?)\s*:\s*['\"]https?://mmbiz[^\s\"']*['\"]"
    
    cdn_urls = re.findall(pattern, content)

    logging.debug(cdn_urls)
    
    if cdn_urls:
        # https://mmbiz.qpic.cn/mmbiz_jpg/AicOhKNCfiaD9SHrapreD260eWviaANiaB100VoiasAeZicAo7Hl0qVTwKfzAUWB5Su4zhuQrtWK4OCwcgCnibUUbaL1g/0?wx_fmt=jpeg
        cleaned_urls = [url.replace(" ","").split(":'")[-1].split("\\")[0] for url in cdn_urls]

        # 去重
        downlist = list(set(cleaned_urls))

        return downlist

    else:
        print("No image URLs found.")
        return None
    

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


def find_title(url: str, soup: BeautifulSoup) -> str:
    tag_title = soup.find(
        'h1', class_='rich_media_title')

    if tag_title:
        return tag_title.get_text().strip()
    else:
        meta_web_title = soup.find("meta", property="og:title")

    if meta_web_title:
        return meta_web_title['content']
    else:
        tag_h2 = soup.find(
            'h2', class_='weui-msg__title title')

    if tag_h2:
        return tag_h2.get_text()
    else:
        tag_div = soup.find(
            'div', class_='weui-msg__title warn'
        )

    if tag_div:
        return tag_div.get_text()
    else:
        tag_script = soup.find('script')

    if tag_script:
        script_content = tag_script.string
        if 'Weixin Official Accounts Platform' in script_content:
            return 'Weixin Official Accounts Platform'
        else:
            '革命尚未成功 同志仍需努力 （未能识别标题，请修改代码）'
            logging.error(url, '未能识别标题')
    else:
        return '革命尚未成功 同志仍需努力 （未能识别标题，请修改代码）'


def rillaget(url: str, folder_path: str, header: str) -> None:
    try:
        response = requests.get(url, headers=header, stream=True, timeout=30)

        # Check if response is successful
        if response.status_code == 200:

            # Figure out image real format
            content_type_name = response.headers.get('Content-Type')
            image_format = content_type_name.split('/')[-1]

            filename = ".".join([url.split("/")[-2], image_format])
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
            logging.error(
                f"Failed to download {url}. HTTP Status Code: {response.status_code}")

    except OSError as f:
        # "Cannot create a file when that file already exists"
        print(f)
        logging.error(f)

    except Exception as e:
        print(f"Error occurred while downloading {url}:\n{str(e)}")
        logging.error(f"Error occurred while downloading {url}:\n{str(e)}")


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


def rename_to_md5(filepath):
    file_name = filepath.split("\\")[-1].split(".")[0]
    new_name = get_md5(filepath)
    new_path = filepath.replace(file_name, new_name)
    try:
        os.rename(filepath, new_path)
    except FileExistsError:
        os.remove(filepath)


def get_md5(filepath):
    # Open,close, read file and calculate MD5 on its contents
    with open(filepath, 'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()
        # pipe contents of the file through
        md5_returned = hashlib.md5(data).hexdigest()

    # Finally compare original MD5 with freshly calculated
    return md5_returned


def webp_to_png_and_fix_gif(folder_path):
    for file in os.listdir(folder_path):
        if ".webp" in file:
            webp_path = os.path.join(folder_path, file)
            print(f"Found Webp! {webp_path}")
            logging.info(f"Found Webp! {webp_path}")
            png_path = webp_path.replace('webp', 'png')
            cmd = f'{STATIC} "{webp_path}" -o "{png_path}"'
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print("Error occurred:", result.stderr.decode())
                logging.error("Error occurred:", result.stderr.decode())
            else:
                os.remove(webp_path)

        if ".gif" in file:
            gif_path = os.path.join(folder_path, file)
            temp_path = os.path.join(folder_path, 'temp.gif')
            print(f"Found Gif! {file}")
            logging.info(f"Found Gif! {file}")
            cmd = f'ffmpeg -i "{gif_path}" -y "{temp_path}"'
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print("Error occurred:", result.stderr.decode())
                logging.error("Error occurred:", result.stderr.decode())
            else:
                os.replace(temp_path, gif_path)
                

def normal():
    for index, url in enumerate(URLS, start=1):

        soup, content = get_soup_from_webpage(url, HEADER, timeout=15)

        title = find_title(url, soup)

        if title == 'Weixin Official Accounts Platform':
            logging.error("疑似遇到服务器抽风，等待5秒钟后重试")
            logging.error(url)
            logging.error(title)
            print("疑似遇到服务器抽风，等待5秒钟后重试")
            time.sleep(5)
            soup, content = get_soup_from_webpage(url, HEADER, timeout=15)
            title = find_title(url, soup)

        gfw_title = [
            "The content has been deleted by the author.",
            "This account has been deleted by the owner. Unable to view the content.",
            "该内容已被发布者删除",
            "此账号已被屏蔽, 内容无法查看",
            "此内容因违规无法查看",
        ]

        if title.strip() in gfw_title:  # 此内容因违规无法查看前后有空段
            print(f"  {index} 来晚了，内容被和谐了。（；´д｀）ゞ  ".center(78, "#"))
            logging.error(f"{title}  {url}  {index} 来晚了，内容被和谐了。（；´д｀）ゞ  ".center(78, "#"))
            print(title)
            print(url)
            print()
            continue

        if title == "革命尚未成功 同志仍需努力 （未能识别标题，请修改代码）":
            print(soup)
            break

        print(index, title, url)
        logging.info(index)
        logging.info(title)
        logging.info(url)

        # downlist = extract_image_url(soup)
        # if not downlist:
        #     print("cdn")
        #     downlist = extract_image_from_cdn_version_page(content)

        downlist = extract_image_using_re_only(content)
        if not downlist:
            print("wtf, chatGPT?!")


        logging.info(downlist)

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
        logging.info(f"共找到{len(downlist)}张图片")

        threads = []
        for img_url in downlist:
            t = Thread(target=rillaget, args=[img_url, folder_path, HEADER])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        # Check and convert WebP to PNG and also fix Gif
        webp_to_png_and_fix_gif(folder_path)
        print()


if __name__ == '__main__':
    normal()

