import os
import requests
import time
from bs4 import BeautifulSoup
from threading import Thread

# 2022年3月31日
# 下载知乎上的一些图片合辑，如“课代表整理”之类的图片的代码


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
}

QUESTION = "https://www.zhihu.com/question/60836727/answer/2411871331"


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


def make_name_valid(validname):
    validname = validname.replace('\\', '_')
    validname = validname.replace('/', '_')
    validname = validname.replace(':', '_')
    validname = validname.replace('*', '_')
    validname = validname.replace('?', '_')
    validname = validname.replace('"', '_')
    validname = validname.replace('<', '_')
    validname = validname.replace('>', '_')
    validname = validname.replace('|', '_')
    validname = validname.replace('\t', '_')
    validname = validname.replace('\r', '_')
    validname = validname.replace('\n', '_')
    validname = validname.replace('\xa0', '_')
    validname = validname.replace("\u200b", "_")
    validname = validname.strip()
    return validname


def rillaget(url, dir_name, header):
    filename = url.split("/")[-1]
    filename = make_name_valid(filename)
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
    return soup


def find_title_of_the_main_post(soup):
    return soup.title.get_text()


def collect_cards_inside_question(soup):
    questions_links = []
    div_a_LinkCard = soup.find_all('a', class_="LinkCard new")
    for each_card in div_a_LinkCard:
        hyperlink_LinkCard = each_card.get('href')
        questions_links.append(hyperlink_LinkCard)
    return questions_links


def extract_images_from_post(soup):
    downlist = []
    div_img_origin_image = soup.find_all('img', class_="origin_image")
    for element in div_img_origin_image:
        image_raw = element.get('data-original')
        image_url = image_raw.split("?")[0]
        downlist.append(image_url)
    return downlist


def find_author(soup):
    div_AuthorInfo = soup.find('span', class_="UserLink AuthorInfo-name")
    post_author = div_AuthorInfo.get_text().strip()
    post_author = make_name_valid(post_author)
    return post_author


def main():

    # 获取课代表帖中的所有链接
    main_post_soup = get_soup_from_webpage(QUESTION, HEADER, 25)
    print(QUESTION)  # 打印该帖地址
    print(find_title_of_the_main_post(main_post_soup))  # 打印该帖标题
    print("\n", "~~"*70, "\n")  # 打印分隔线
    questions_links = collect_cards_inside_question(main_post_soup)
    print(f"找到{len(questions_links)}个链接，正依次打开")

    # 如果确实找到链接，就新建一个文件夹，准备开始下载
    if not len(questions_links):
        return
    else:
        mainfolder = " ".join([QUESTION.split(
            '/')[-1], find_title_of_the_main_post(main_post_soup).replace(" - 知乎", "")])
        mainfolder = make_name_valid(mainfolder).replace("？", "").strip()
        if not os.path.exists(mainfolder):
            os.makedirs(mainfolder)

    # 依次获取每个链接中的原图的地址
    for each_individual_question in questions_links:
        particular_question_soup = get_soup_from_webpage(
            each_individual_question, HEADER, 25)
        dirname = find_author(particular_question_soup)
        print(f"\n正在打开 {each_individual_question}\n该帖作者是{dirname}\n")  # 打印该链接帖地址
        downlist = extract_images_from_post(particular_question_soup)

        # 下载 获取的图片 并 保存 在该帖作者id的文件夹下， 方便后续整理
        author_folder = os.path.join(mainfolder, dirname)
        if not os.path.exists(author_folder):
            os.makedirs(author_folder)

        # 进行多线程下载
        threads = []
        for image_url in downlist:
            thread = Thread(target=rillaget, args=[
                            image_url, author_folder, HEADER])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        
        # 等待几秒钟，让服务器休息一下
        time.sleep(2)


if __name__ == '__main__':
    os.chdir(r"D:\RMT\zhihu question")
    main()
    print("～～完结撒花～～")
