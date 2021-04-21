import os 
import time
import requests
import re
from bs4 import BeautifulSoup

'''

This is the single file version.
Download one page a time, and you have to manually change the url each time.

'''


URL = "https://www.dgtle.com/inst-1689143-1.html"

header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

for i in range(1,2):
    try:
        # request=urllib.request.Request(URL,headers=header)
        # content = urllib.request.urlopen(request).read()
        response = requests.get(URL,headers=header)
        content = response.text
        # data = content.decode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        # Print Title of the page
        title = soup.title.get_text()
        print(title)
        # Extract the hi resolution image url
        re_img_url = r"(?<=img src=\").+?dgtle_img.+?(?=\")"
        urls = re.findall(re_img_url, content)
        downlist = []
        for url in urls:
            url_hi = url.replace('_1800_500','')
            downlist.append(url_hi)
            if 'inst' in URL:
                # inst author
                name = soup.select('div.own-img > div:nth-child(2) > span:nth-child(1)')
                title = soup.title.get_text()
                for n1 in name:
                    dir_name = n1.get_text()
            elif 'article' in URL:
                # article author
                name = soup.select('.author')
                title = soup.title.get_text()
                for n2 in name:
                    dir_name = n2.get_text()
            else:
                # Just in case a new format is shown
                print('There is no key words in URL, please add new code to fix it.')
    except:
        print("Links extracting failed..")
        print("Wait for 5 seconds")
        time.sleep(5)
        print("Continue...")
        continue
    print(dir_name)

# Create the folder with the author's id
for url in downlist:
    file_name = url.split("/")[-1]
    try:
        response = requests.get(url, verify=False, headers=header, timeout=15)
        if response.status_code == 200:
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)        
        total_path = dir_name + '/' + file_name
        if len(response.content) == int(response.headers['Content-Length']):

            with open(total_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                f.close()
        else:
            print("Image not complete")
    except:
        print("Connection dropped..")
        print("Wait for 5 seconds")
        time.sleep(5)
        print("Continue...")
        continue
