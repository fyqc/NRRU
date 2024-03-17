# IIS部署日志站点时出现的UTF8文件乱码问题及解决

## 问题产生原因

为方便查看线上问题日志，在服务器的`IIS`上新建了一个站点，根目录指向log目录，并开始了目录浏览；
嗯，可以进入网站，看到目录列表了，找到一个txt文件，点击看看日志，咦，怎么里面的中文变成了#%$@

好吧，以前经常处理这个问题，就是点击chrome的菜单=》更多工具=》编码=》UTF8就可以解决，
我熟练的打开了菜单，我找，找，找，编码菜单到哪去了？？？什么鬼？
原来chrome认为自己的自动检测功能很牛B，把编码选项给去掉了，去掉了……

怎么办？只能从IIS服务器着手，查了半天资料，找到一个解决方案，在站点`根目录`下的Web.config添加如下配置：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <httpProtocol>
      <customHeaders>
        <add name="Content-Type" value="text/plain; charset=utf-8" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
```

嗯，果然，txt文件不`乱码`了。
等下，目录列表怎么变成html了？？？
上面配置里那个plain搞的鬼，改成text/html怎么样？
我去，txt文件又变成html来解析了，这样会有xss攻击的可能啊……
改成如下，没有任何效果：

```xml
<add name="Content-Type" value="charset=utf-8" />
```

最终还是自己摸索了半天，找到了解决方案，还是改web.config，内容如下，简单说就是只设置txt扩展名的mimetype：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <directoryBrowse enabled="true" showFlags="Date, Time, Size, Extension, LongDate" />
        <staticContent>
            <remove fileExtension=".txt" />
            <mimeMap fileExtension=".txt" mimeType="text/plain;charset=utf-8" />
        </staticContent>
    </system.webServer>
</configuration>
```
                        
原文链接：[https://blog.csdn.net/youbl/article/details/78028092](https://blog.csdn.net/youbl/article/details/78028092)

