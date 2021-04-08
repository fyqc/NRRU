# 给mp4视频添加封面图片

发现在下载B站这方面，you-get明显比youtube-dl好用，不用再单独用ffmpeg把flv转化成mp4了。省心省事儿。

但是遗憾的是视频里面没有预览的thumbnail图片，显得不太美观。就继续Google一下，发现这个困扰在我之前早就有人解决过了。

IT界的名言，不要重复发明轮子，拿来用就好，看了Stackflow上的回答，用了以下的命令行轻松解决问题。

```powershell

    ffmpeg -i 01.mp4 -i 01.jpg -map 1 -map 0 -c copy -disposition:0 attached_pic out.mp4
```


| 参数  |含义 |
|----------------|-------------------------------|
|01.mp4 |`待添加的视频`            |
|01.jpg |`待添加的图片`            |
|out.mp4 |`生成的文件`|


![image](https://raw.githubusercontent.com/fyqc/NRRU/main/IMG/%E7%BB%99mp4%E8%A7%86%E9%A2%91%E6%B7%BB%E5%8A%A0%E5%B0%81%E9%9D%A2%E5%9B%BE%E7%89%87.PNG)
