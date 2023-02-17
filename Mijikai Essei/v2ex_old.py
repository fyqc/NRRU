import os
import requests
from bs4 import BeautifulSoup

# 一个V站翻页器，用于网页浏览时找到上次看过的旧帖的位置
# 完成时发现一个新的方法，该方案不如新方案高效好用，遂留在这里以作纪念
# 2023年2月16日

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
}

# https://www.v2ex.com/t/875455#reply12
TARGET = 875455  # 上一次看过的帖子的ID号

# https://www.v2ex.com/recent?p=1376
POTENTIAL = 1390  # 大致位置


def url_trim(url):
    return 'https://www.v2ex.com/t/' + str(TARGET)


def url_pool(POTENTIAL, offset=1):
    url_list = []
    for num in range(POTENTIAL, POTENTIAL + offset):
        url_list.append('https://www.v2ex.com/recent?p=' + str(num))
    return url_list


def get_soup_from_webpage(url, header, timeout=None):
    response = requests.get(url, headers=header, timeout=timeout)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()
    return soup


def main():
    offset = 1
    found = False
    while found == False and offset <= 50:  # 根据日期酌情调整该数字
        url_list = url_pool(POTENTIAL, offset)
        for url in url_list:
            soup = get_soup_from_webpage(url, HEADER, 15)
            div_main = soup.find('div', id="Main")
            a_topic_link = div_main.find_all('a', class_="topic-link")
            for n in a_topic_link:
                # /t/876000
                # https://www.v2ex.com/t/876061#reply3
                t_number = n.get('href').split("#")[0].replace("/t/", "")

                if t_number == str(TARGET):
                    topic_full_url = 'https://www.v2ex.com/t/' + t_number
                    page_number = (url.split("=")[1])
                    print(f"找到了，在第{page_number}页， 地址为{topic_full_url}")
                    found = True
                    break
            if found == True:
                break
            offset += 1

if __name__ == '__main__':
    main()
