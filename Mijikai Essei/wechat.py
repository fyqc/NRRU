import hashlib
import json
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
从icloud那里把URL复制到txt文件中
然后执行，就可以在目标文件夹中生成以标题为文件夹名的文件夹，里面是帖子中的图片
"""

# 2024年11月4日
# 重新启用数据库
# 不再将重复文件移入临时文件夹，直接删除
# 将原先的列表改进为txt文档
# 发现漏下了一些图片，遂使用正则表达式一把梭

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    # level=logging.DEBUG,
    level=logging.INFO,
    handlers=[logging.FileHandler(
        filename='tencent.log', mode='w', encoding='utf-8')]
)

"""
日志级别     使用场景
DEBUG 	    最低级别。用于小细节。通常只有在诊断问题时，你才会关心这些消息
INFO 	    用于记录程序中一般事件的信息，或确认一切工作正常
WARNING 	用于表示可能的问题，它不会阻止程序的工作，但将来可能会
ERROR 	    用于记录错误，它导致程序做某事失败
CRITICAL 	最高级别。用于表示致命的错误，它导致或将要导致程序完全停止工作

日志级别重要程度逐次提高，logging分别提供了5个对应级别的方法。默认情况下日志的级别是WARGING， 低于WARING的日志信息都不会输出。
从最不重要到最重要。利用不同的日志函数，消息可以按某个级别记入日志。
"""


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
    'Accept-Language': 'en-US,en;q=0.5',
}

STATIC = r"F:\Lab\libwebp-1.4.0-windows-x64\bin\dwebp.exe"
SAVE_DIRECTORY = r"D:\RMT\Tencent Wechat\tecent public"
DATABSE = r"D:\RMT\Tencent Wechat\Wechat\wc.json"
ICLOUD = r"D:\RMT\Tencent Wechat\Wechat\download.txt"


def get_urls_from_download_txt(ICLOUD):
    urls = []
    with open(ICLOUD, 'r') as f:
        content = f.readlines()
        for line in content:
            if line.startswith('https'):
                urls.append(line.strip('\n'))
    return urls


def get_soup_from_localhtml(webpage):
    with open(webpage, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, features='lxml')

    return soup, content


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
    validname = validname.replace('📷', '').replace('🎈', '').replace('😜', '')
    # 在 Windows 系统中建立文件夹时名字的最后不能是“．”，不论你加多少个点，都会被 Windows 忽略。
    validname = validname.rstrip(".")
    validname = validname.strip()
    return validname


def extract_image_using_re_only(content: str) -> list:
    pattern = r"(?:['\"]?cdn_url['\"]?)\s*:\s*['\"]https?://mmbiz[^\s\"']*['\"]"

    raw_urls = re.findall(pattern, content)

    logging.debug(raw_urls)

    if raw_urls:
        pure_urls = [url.replace(" ", "").split(
            ":'")[-1].split("\\")[0] for url in raw_urls]

        # 去重
        downlist = list(set(pure_urls))

        return downlist

    else:
        # 早期链接形式为
        # data-src="https://mmbiz.qpic.cn/sz_mmbiz_png/MVPvEL7Qg0G6NN3oSIm4CuPDWGQo3LX6fRzicLvdbmssAa1qwOibrXjeNicbziaca2K5RQFZg6X5NdUVXYvK9rkiaBA/640?wx_fmt=png"
        pattern = r"(?:data-src=['\"]?)\s*['\"]https?://mmbiz[^\s\"']*['\"]"

        raw_urls = re.findall(pattern, content)

        print("发现古早链接形式，使用后备解析方法。")
        logging.info("发现古早链接形式，使用后备解析方法。")
        logging.debug(f"2nd raw_urls:\n{raw_urls}")

        if raw_urls:
            pure_urls = [url.split("data-src=")[-1].replace('"', '')
                         for url in raw_urls]

            # 去重
            downlist = list(set(pure_urls))

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
            rename_to_sha256(total_path)

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


def rename_to_sha256(filepath):
    file_name = filepath.split("\\")[-1].split(".")[0]
    new_name = get_sha256(filepath)
    new_path = filepath.replace(file_name, new_name)
    try:
        os.rename(filepath, new_path)
    except FileExistsError:
        os.remove(filepath)


def get_sha256(filepath):
    # Open,close, read file and calculate sha256 on its contents
    with open(filepath, 'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()
        # pipe contents of the file through
        sha256_returned = hashlib.sha256(data).hexdigest()

    # Finally compare original sha256 with freshly calculated
    return sha256_returned


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
                rename_to_sha256(png_path)

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
                rename_to_sha256(gif_path)


def delete_if_found_duplicate(folder_path, existing_file_dict):
    for file in os.listdir(folder_path):
        f_hash = file.split(".")[0]
        if f_hash in existing_file_dict:
            print(f"{existing_file_dict[f_hash]} 曾经下载过，hash值是 {f_hash}，删除之")
            logging.warning(
                f"{existing_file_dict[f_hash]} 曾经下载过，hash值是 {f_hash}，删除之")
            # 删除！！！！
            os.remove(os.path.join(folder_path, file))
        else:
            existing_file_dict[f_hash] = os.path.join(folder_path, file)

    # 假如删除完毕，该文件夹为空，则直接删除整个文件夹
    if len(os.listdir(folder_path)) == 0:
        print(f"{folder_path} 为空，删除之")
        logging.warning(f"{folder_path} 为空，删除之")
        # 删除！！！！
        shutil.rmtree(folder_path)


def read_json() -> dict:
    '''
    从DATABASE中读取字典文件
    '''
    with open(DATABSE, 'r') as f:
        return json.load(f)


def write_json(stored_dict: dict) -> None:
    with open(DATABSE, 'w') as f:
        json.dump(stored_dict, f)


def resume_from_breakpoint(existing_file_dict):
    '''
    断点续传功能
    '''
    is_rfb_needed = False
    # 先检测一下看看SAVE_DIRECTORY文件夹里面有没有东西
    with os.scandir(SAVE_DIRECTORY) as it:
        if any(it):
            print("检测到SAVE_DIRECTORY文件夹中存在文件，可能是上次任务中断引起，将启动断点续传功能")
            logging.info("检测到SAVE_DIRECTORY文件夹中存在文件，可能是上次任务中断引起，将启动断点续传功能")
            is_rfb_needed = True

    if is_rfb_needed:
        for author, _, files in os.walk(SAVE_DIRECTORY):
            for file in files:
                file_path = os.path.join(author, file)
                f_hash = file.split(".")[0]
                existing_file_dict[f_hash] = file_path


def play():
    # 获得要下载的文件的url列表
    URLS = get_urls_from_download_txt(ICLOUD)

    if duplicate_filter:
        # 从存档中读取所有文件的Hash值
        print("正在读取存档，请稍候")
        existing_file_dict = read_json()

        # 断点续传功能，把SAVE_DIRECTORY文件夹里面的文件的Hash值也添加到字典中去
        resume_from_breakpoint(existing_file_dict)

    # 正式开始下载工作
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
            logging.error(
                f"{title}  {url}  {index} 来晚了，内容被和谐了。（；´д｀）ゞ  ".center(78, "#"))
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

        downlist = extract_image_using_re_only(content)
        if not downlist:
            print("是时候去咨询一下chatGPT了")
            logging.critical("未能发现任何链接，是时候去咨询一下chatGPT了")
            continue

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

        if duplicate_filter:
            # Figure out if any file has been duplicated with database record
            delete_if_found_duplicate(folder_path, existing_file_dict)

        print()

    if duplicate_filter:
        # 将新的所有文件的Hash值写回到存档中
        print("正在写入存档，请稍候")
        write_json(existing_file_dict)


class NotUseAnymore():
    def test():
        print()

    def get_md5(filepath):
        # Open,close, read file and calculate MD5 on its contents
        with open(filepath, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_returned = hashlib.md5(data).hexdigest()

        # Finally compare original MD5 with freshly calculated
        return md5_returned

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
        logging.info(raw_down_list)
        cleaned_urls = [url.split("\\")[0] for url in raw_down_list]

        if raw_down_list:
            # 去重
            downlist = list(set(cleaned_urls))
            return downlist

        else:
            print("No image URLs found.")
            return None

    def rillatest():
        print("让我们荡起双桨")

    def input_url():
        print('https://mp.weixin.qq.com/s/KAI2s49-pXLtPX7FudnRQg')
        url = input('输入要下载的微信公众号的网址，格式如上： ')
        return url

    def try_soup_ten_times(url, header=HEADER):
        soup_attemp = 0
        success_status = False
        while soup_attemp < 10 and not success_status:
            try:
                soup, content = get_soup_from_webpage(url, header, timeout=15)
                title = find_title(url, soup)

                if title == "autorestart":
                    print(f"when opening\n{url}, error occur:")
                success_status = True

            except:
                soup_attemp += 1
                print("Seems the network is not very stable...")
                print("Let's wait for 5 seconds.")
                time.sleep(5)
                print("Ok, let's try again.")
                if soup_attemp == 10:
                    print("Well, let it go.")
                    return ("404", "404")
        return soup, content, title

    def big_pick():
        for file in os.listdir(SAVE_DIRECTORY):
            file_path = os.path.join(SAVE_DIRECTORY, file)
            with Image.open(file_path) as picture:
                image_width, image_height = picture.size
            if image_height > 1001 and image_width > 1001:
                shutil.move(file_path, r'D:\RMT\Tencent Wechat\Review')

    def cwtp(total_path):
        # Conver WebP to PNG
        if '.webp' in total_path:
            print(f"Found Webp! {repr(total_path)}")
            webp_to_png_and_fix_gif(repr(total_path))

    def find_filename(img_url: str) -> str:
        """
        2024年7月25日
        决定重写，把判断格式的逻辑放到下载器里面去
        """
        if 'mmbiz.qpic.cn' in img_url:
            return img_url.split("/")[-2]

    def Abandon():
        # for author, _, files in os.walk(SAVE_DIRECTORY):
        #     for file in files:
        #         file_path = os.path.join(author, file)
        #         f_hash = file.split(".")[0]
        #         existing_file_dict[f_hash] = file_path

        # # 把已经精选过了的文件也算进来
        # for title, _, files in os.walk(r"D:\RMT\Tencent Wechat\Wechat"):
        #     for file in files:
        #         if '.txt' in file:
        #             continue
        #         if '.json' in file:
        #             continue
        #         file_path = os.path.join(title, file)
        #         f_hash = file.split(".")[0]
        #         existing_file_dict[f_hash] = file_path

        # write_json(existing_file_dict)
        pass


if __name__ == '__main__':
    # 过滤器开关
    duplicate_filter = True
    play()
