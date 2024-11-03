import logging
import os
import re
import requests
import time
from bs4 import BeautifulSoup
from threading import Thread

# 2024年11月3日
# 用于爬取ChipHell论坛里的图片

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s - %(lineno)s',
    level=logging.INFO,
    # level=logging.DEBUG,
    handlers=[logging.FileHandler(
        filename='ch.log', mode='a', encoding='utf-8')]
)


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
    'Accept-Language': 'en-US,en;q=0.5',
}

SAVE_DIRECTORY = r"D:\Chiphell"


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
    validname = validname.replace('\xa0', '')
    validname = validname.replace('～', '')
    validname = validname.rstrip(".")
    validname = validname.strip()
    return validname


def extract_image_using_re_only(content: str) -> list:
    pattern = r"\s*https?://static.chiphell.com/forum[^\s\"']*"
    raw_urls = re.findall(pattern, content)
    if raw_urls:
        return list(set(raw_urls))
    else:
        print("No image URLs found.")
        return None


def find_title(soup: BeautifulSoup) -> str:
    return soup.title.get_text()


def rillaget(url: str, folder_path: str, header: str) -> None:
    try:
        response = requests.get(url, headers=header, stream=True, timeout=30)

        # Check if response is successful
        if response.status_code == 200:

            # Figure out image real format
            content_type_name = response.headers.get('Content-Type')
            image_format = content_type_name.split('/')[-1]

            filename = url.split("/")[-1]
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


def play(url):
    soup, content = get_soup_from_webpage(url, HEADER, 15)
    title = find_title(soup)
    print(title)
    logging.info(title)
    downlist = extract_image_using_re_only(content)
    logging.info(downlist)
    folder_path = os.path.join(
            SAVE_DIRECTORY, make_name_valid(title))
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
        

if __name__ == '__main__':
    # https://www.chiphell.com/thread-2596721-1-1.html
    url = ""
    play(url)

