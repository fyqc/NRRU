# 从YouTube下载mp3

**把youtube的链接换成需要的链接**：

    youtube-dl -x --audio-format mp3 https://www.youtube.com/watch?v=z7LGqmBY79E

*有时候需要在YouTube的链接上加引号*，如：

    youtube-dl -x --audio-format mp3 "https://www.youtube.com/watch?v=z7LGqmBY79E"
---

## 准备工作

1. ### 下载安装 youtube-dl

youtube-dl官网：https://github.com/ytdl-org/youtube-dl

    pip install --upgrade youtube_dl

![image](https://raw.githubusercontent.com/fyqc/NRRU/main/IMG/%E4%BB%8EYouTube%E4%B8%8B%E8%BD%BDmp3_1.png)


2. ### 分别安装ffmpeg和ffprobe

![image](https://raw.githubusercontent.com/fyqc/NRRU/main/IMG/%E4%BB%8EYouTube%E4%B8%8B%E8%BD%BDmp3_2.png)

![image](https://raw.githubusercontent.com/fyqc/NRRU/main/IMG/%E4%BB%8EYouTube%E4%B8%8B%E8%BD%BDmp3_3.png)

3. ### 下载LIBAV

选择对应的版本下载。

得到一个7z的压缩包.

解压后把bin文件夹里面的所有东西复制到你的youtube-dl.exe 所在的文件夹

默认在本机的用户文件夹里面，Windows 7的话是在开始菜单右上角里找到自己的User文件夹，具体路径如下

> C:\Users\fyq\AppData\Local\Programs\Python\Python38-32\Scripts


将bin文件夹里面的所有文件选中并复制到youtube-dl.exe所在的文件夹里

---

回到cmd窗口，按以下格式输入即可得到mp3



    youtube-dl -x --audio-format mp3 https://www.youtube.com/watch?v=z7LGqmBY79E

![image](https://raw.githubusercontent.com/fyqc/NRRU/main/IMG/%E4%BB%8EYouTube%E4%B8%8B%E8%BD%BDmp3_4.png) 

下载下来的mp3默认在User文件中

    C:\Users\fyq\
