import os
import requests
from bs4 import BeautifulSoup

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
}

# V站翻页器
# 利用快捷方式和“https://www.v2ex.com/recent?p=1”的标题来计算之前的快捷方式所在的帖子现在的位置
# 所在目录应有一唯一的快捷方式，类似于以下格式：
# V2EX › 最近的主题 1401_30031
# 标题则应为如下格式：
# V2EX › 最近的主题 1401/30031

# 2023年2月17日


def get_soup_from_webpage(url, header, timeout=None):
    response = requests.get(url, headers=header, timeout=timeout)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()
    return soup

def shortcut_method():
    # 读取手动保存的快捷方式的标题以获取上次看到的页数以及上一次的总页数
    for (_, _, filenames) in os.walk(os.getcwd()):
        if len(filenames) == 2 and filenames[0].endswith('.URL'):
            key_numbers = filenames[0].replace(
                "V2EX › 最近的主题 ", "").replace(".URL", "")
            old_current_page, old_total_page = key_numbers.split("_")

    # 从 https://www.v2ex.com/recent?p=1 读取本次最新的总页数
    soup = get_soup_from_webpage("https://www.v2ex.com/recent?p=1", HEADER, 15)
    title = soup.title.get_text().replace("V2EX › 最近的主题 ", "").replace(".URL", "")
    new_total_page = title.split("/")[1]


    # 计算偏移值修正后的新起始位置
    offset = int(new_total_page) - int(old_total_page)
    new_position = int(old_current_page) + offset
    print(f"请看第{new_position}页")


if __name__ == '__main__':
    shortcut_method()
    input("")
