import os
import requests
from bs4 import BeautifulSoup

# 用于Bohaishibei某一个博文的批量图片保存
# 2023年2月15日

HEADER = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 "
          "(KHTML, like Gecko) Version/15.0 Safari/605.1.15",
          }


ADDRESS = "https://www.bohaishibei.com/post/80469/"


def get_soup_from_webpage(url, header, timeout=None):
    response = requests.get(url, headers=header, timeout=timeout)
    # 这里的编码应根据网页源码指定字符集做相应修改
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    # 抛弃网页中的垃圾元素，加快处理速度
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()

    return soup


def extract_images_from_bohaishibei_post(soup):
    downlist = []
    div_entry_content = soup.find('div', class_="entry-content")
    img_src = div_entry_content.find_all('img')
    for attr_src in img_src:
        image_url = attr_src.get('src')
        downlist.append(image_url)

    return downlist


def find_title_of_bohaishibei_post(soup):
    return soup.title.get_text().replace(" – 博海拾贝", "").strip()


def rillaget(url, dir_name, header):
    filename = url.split('/')[-1]
    total_path = os.path.join(dir_name, filename)

    attempts = 0
    success = False
    while attempts < 5 and not success:
    
        try:
            response = requests.get(url, headers=header, timeout=8)
            with open(total_path, 'wb') as f:
                f.write(response.content)
                print(f"{filename}  下载成功")
                success = True

        except Exception as e:
            print(f"{url} 发生异常：\n{e}")
            attempts += 1
    
    if attempts == 5:
        print(f"{filename} Failed to downloaded.")

if __name__ == '__main__':
    soup = get_soup_from_webpage(ADDRESS, HEADER)
    title = find_title_of_bohaishibei_post(soup)
    downlist = extract_images_from_bohaishibei_post(soup)
    for url in downlist:
        rillaget(url, "D:\PyTrial", HEADER)

