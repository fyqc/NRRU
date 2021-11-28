import os
import requests
import random
import time
from bs4 import BeautifulSoup
from threading import Thread


"""2021年11月27日"""


def get_soup_from_webpage(url, header):
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    # 2021年11月11日加入的新检测功能，用来对付宝塔防火墙的自动跳转
    if soup.title.get_text() == '检测中':
        # 把故意添加在</html>外面的的js脚本弄到里面来，以便让BeautifulSoup可以处理之
        html = response.text.replace('</html>', '') + '</html>'
        url = find_redirect_url_from_script(html)
        print(f"URL被重定向至:")
        print(url)
        header['Referer'] = url
        return get_soup_from_webpage(url, header)

    else:
        # 抛弃网页中的垃圾元素，加快处理速度
        for script in soup.find_all("script"):
            script.decompose()
        for style in soup.find_all("style"):
            style.decompose()
        return soup


def lets_wait(timer=20):
    while timer > 0:
        time.sleep(1)
        print(f"请等待{timer}秒")
        timer -= 1
    print("等待结束，让我们继续")


def get_dir(soup):
    return soup.title.get_text().split("丨")[0].strip()


def make_list(soup):
    '''从『归档』处获得所有的帖子的列表'''
    postdict = {}
    div_archives = soup.find('div', class_='archives')
    tags_a = div_archives.find_all('a')
    # url_pre = 'https://www.vmgirls.com/'
    for tag in tags_a:
        post_num_html = tag['href']
        if '17984' in post_num_html:  # <<<<<<<<<<<<<<<<<  2021年11月27日 采集到这里停止了
            break
        post_title = tag.get_text()
        # posturl = url_pre + post_num_html
        posturl = post_num_html
        # 这里要把第一项，也就是唯一一个带#的项滤掉
        # 'https://www.vmgirls.com/#': '全部展开/收缩'
        if '#' in posturl:
            continue
        postdict[posturl] = post_title
    return postdict


def download_single_post(single_post_soup, header):
    '''解析单页面内的所有图片地址并调用下载器多线程下载'''

    downlist = extract_image_url(single_post_soup)
    if not downlist:
        print("这个帖子不存在图片，跳过～～")
    else:
        downlist = list(set(downlist))  # 对downlist去重
        # print(downlist)
        dir_name = 'D:/RMT/TRY/vmg/' + get_dir(single_post_soup)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)  # 建立文件夹
        threads = []
        for url in downlist:
            if not str(url).startswith('https://'):
                print("混进来奇怪的url: " + url)
                continue
            # src="//t.cdn.ink/image/2021/11/x2021110119071930.jpeg.pagespeed.ic.3JAJcN96aD.jpg"
            if "pagespeed.ic" in url:  # 发现于2021年11月22日
                print("混进来奇怪的url: " + url)
                continue
            t = Thread(target=rillaget, args=[url, dir_name, header])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()


def extract_image_url(soup):
    '''从网页soup中提纯原图url'''
    downlist = []

    # CASE 1 - ANY IMAGE NEWER THAN 17054
    div_nc_light_gallery = soup.find('div', class_="nc-light-gallery")
    a = div_nc_light_gallery.find_all('a')

    for n in a:
        img_url_incomplete = n.get('href')
        # 居然还有这种东西跑出来干扰
        # tag/%e6%91%84%e5%bd%b1/
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = str('https:' + img_url_incomplete).replace("-scaled", "")
            downlist.append(img_url)

    # CASE 2 ANY IMAGE OLDER AROUND 2239
    img = div_nc_light_gallery.find_all('img')
    for n in img:
        img_url_incomplete = n.get('src')
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = str('https:' + img_url_incomplete).replace("-scaled", "")
            downlist.append(img_url)

    return downlist


def i_dnt_wanna_cache(url):
    '''向URL添加随机伪参数以防止缓存命中，如在 URL 后添加时间戳'''
    false_random_number = random.randint(1533834270359, 1553834270359)
    return "".join([url, '?_=', str(false_random_number)])


def rillaget(url, dir_name, header):
    filename = url.split("/")[-1]
    total_path = dir_name + '/' + filename

    attempts = 0
    success = False

    while success is not True and attempts < 8:
        time.sleep(random.uniform(1.1, 3.4))  # 添加随机等待，避免服务器炸锅
        try:
            response = requests.get(
                i_dnt_wanna_cache(url), headers=header, timeout=5)
        except:
            print(f"{filename} 下载遇到困难，网络连接不畅，再试一次")
            try:
                response = requests.get(
                    i_dnt_wanna_cache(url), headers=header, timeout=5)
            except:
                print(f'{filename} 下载实在困难')
                attempts += 1
                continue

        if 'Content-Length' in response.headers:
            if len(response.content) == int(response.headers['Content-Length']):
                with open(total_path, 'wb') as fd:
                    for chunk in response.iter_content(1024):
                        fd.write(chunk)
                print(f"{filename}  {len(response.content)//1000}KB  下载成功 ")
                success = True

        elif len(response.content) > 40000:  # 只要有 40KB 就下载
            with open(total_path, 'wb') as fd:
                for chunk in response.iter_content(1024):
                    fd.write(chunk)
            print(
                f"{filename}  {len(response.content)//1000}KB  下载成功  但存在不完整的风险")
            success = True

        else:
            attempts += 1
            print(
                f"{filename} 只有 {len(response.content)}bytes "
                f"再试第{attempts + 1}次 status_code:{response.status_code}")
            lets_wait(attempts*3)

        if attempts == 6:
            # 可能服务器上没有非scale的图片，尝试恢复原文件名再下载
            url = str(url).replace(".jpeg", "-scaled.jpeg")
            url = str(url).replace(".png", "-scaled.png")
            url = str(url).replace(".jpg", "-scaled.jpg")
            url = str(url).replace(".webp", "-scaled.webp")
            # 文件名也要跟着变
            total_path = str(total_path).replace(".jpeg", "-scaled.jpeg")
            total_path = str(total_path).replace(".png", "-scaled.png")
            total_path = str(total_path).replace(".jpg", "-scaled.jpg")
            total_path = str(total_path).replace(".webp", "-scaled.webp")
            print("尝试下载非高清图片")

        if attempts == 8:
            print(f'{filename}  下载失败 status_code:{response.status_code}')


def bring_mms_home(header):
    top_list_soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)

    postdict = make_list(top_list_soup)

    if not postdict:
        print("没有找到新的图片")

    for posturl in postdict:
        print(f'正在打开：  {posturl}  {postdict[posturl]}')

        # 为防止被托管服务器运营商抽中去做莫名其妙的5秒钟的“跳转”，加入以下代码
        single_post_soup = get_soup_from_webpage(posturl, header)
        while get_dir(single_post_soup) != postdict[posturl]:
            print(get_dir(single_post_soup))
            lets_wait()
            single_post_soup = get_soup_from_webpage(posturl, header)
            print(get_dir(single_post_soup))

        download_single_post(single_post_soup, header)


def find_out_url_from_title(foldername, header):
    '''根据 文件夹的名字 返回 网页标题叫这个名字的url列表'''
    print(foldername)
    missed_url_list = []
    soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)
    # 抛弃网页中的垃圾元素，加快处理速度

    postdict = make_list(soup)
    for posturl in postdict:
        if postdict[posturl] == foldername:
            print(posturl)
            missed_url_list.append(posturl)
    return missed_url_list


def makeup(header):
    '''
    查缺补漏
    输入 不完整的图片的文件夹的名字
    返回 重新下载整个文件夹
    '''
    post_url_list = find_out_url_from_title('日系小清新', header)
    for posturl in post_url_list:
        download_single_post(posturl, header)


def find_redirect_url_from_script(html):
    tag_script = BeautifulSoup(html, 'lxml').find_all('script')[-1]
    btwaf = tag_script.string.split("/")[-1].replace('";', '')
    prefix = 'https://www.vmgirls.com/'
    btwaf_url = (prefix + btwaf).strip()  # url中有一个空格，真是令人大跌眼镜
    return btwaf_url


if __name__ == '__main__':
    header = {
        'Referer': 'https://www.vmgirls.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
        ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
    }

    bring_mms_home(header)

    print("～～完结撒花～～")


# TODO 17054 @ 7/19/2021
# TODO 17212 @ 8/29/2021
# TODO 17863 @ 11/10/2021
# TODO 17780 @ 11/22/2021
# TODO 17984 @ 11/27/2021
