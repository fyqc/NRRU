# 用Python把DOC转换成txt的方法

## 需要用Word的VBA将DOC先转换为DOCX，再用Python的python-docx库将docx转为txt  

---

其中，Word的VBA操作在  
[微软官网](https://answers.microsoft.com/en-us/msoffice/forum/all/bulk-convert-doc-files-to-docx-in-word-2016/1c5628bc-c2ea-4072-bb25-56eae952d2c5)  

> You can follow these steps to bulk convert .doc files to .docx.  
1. Put all .doc file to a folder e.g. `D:\doc\`.

2. Open Word and press `“Alt+ F11”` to open the VBA editor.

3. Now click `“Normal”` project and click `“Insert”` > `“Module”` to insert a new module in the project.  
![](https://filestore.community.support.microsoft.com/api/images/b6fe41a6-a1f7-4e84-a8af-d759486271ab)

5. Double click the module to open the editing area and paste the following codes:

```VBA
Sub TranslateDocIntoDocx()
  Dim objWordApplication As New Word.Application
  Dim objWordDocument As Word.Document
  Dim strFile As String
  Dim strFolder As String

  strFolder = "D:\doc\"
  strFile = Dir(strFolder & "*.doc", vbNormal)

  While strFile <> ""
    With objWordApplication      
      Set objWordDocument = .Documents.Open(FileName:=strFolder &strFile, AddToRecentFiles:=False, ReadOnly:=True, Visible:=False)

      With objWordDocument
        .SaveAs FileName:=strFolder & Replace(strFile, "doc", "docx"), FileFormat:=16
        .Close
      End With
    End With
    strFile = Dir()
  Wend   

  Set objWordDocument = Nothing
  Set objWordApplication = Nothing
End Sub
```
![](https://filestore.community.support.microsoft.com/api/images/a0984566-6640-4bc4-baab-d490c57b6d1c)

5. Click “Run” button. Seconds later, you will find all .doc files have been converted to .docx files.
![](https://filestore.community.support.microsoft.com/api/images/91eea8a3-0b24-4551-bacc-e23f4f4f2d06)
![](https://filestore.community.support.microsoft.com/api/images/8911a6d2-4fe7-4a46-a506-6e508427b367)
---

## 这个过程中可能会报错
>Error message in Office when a file is blocked by registry policy settings

解决方案也在[微软官网](https://docs.microsoft.com/en-US/office/troubleshoot/settings/file-blocked-in-office)

>A file is blocked when you open or save the file in a Microsoft Office program. In this situation, you may receive an error message that resembles one of the following:

>You are attempting to open a file that is blocked by your registry policy setting.
>You are attempting to open a file type <File Type> that has been blocked by your File Block settings in the Trust Center.
>You are attempting to open a file that was created in an earlier version of Microsoft Office. This file type is blocked from opening in this version by your registry policy setting.
>You are attempting to save a file that is blocked by your registry policy setting.
>You are attempting to save a file type <File Type> that has been blocked by your File Block settings in the Trust Center.
---
Resolution

To resolve this issue, try the following general resolutions to change the File Block settings to disable the restriction of certain file types:

1.  Select `File` > `Options`.

>  If you cannot open a file in Office, open a blank document to start the Office application. For example, if you cannot open a Word file, open a new document in Word 2016 or later versions to see the option.

2.  In the `Options` window, select `Trust Center` > `Trust Center Settings`.

3.  In the `Trust Center` window, select `File Block Settings`, and then clear the "Open" or "Save" check box for the file type that you want to open or save.  

NOTE:  
> Clear the option means allow user to open or save the file. Check the option means block the file.  

![](https://docs.microsoft.com/en-US/office/troubleshoot/client/settings/media/file-blocked-in-office/trust-center-window.png)

4. Select `OK` two times.

5. Try to open or save the file that was blocked again.
---

## 接下来用Google Colab进行在线操作：  

### 先安装python-docx库
> !pip install python-docx

### 关联Google Drive到Colab实例：
```python
from google.colab import drive
drive.mount('/content/drive')
```

`运行`后，授权

就会发现content文件夹下面多了一个drive文件夹，再打开就是My Drive,My Drive 文件夹里面的就是在云盘里面的东西了。  

以后使用云盘里面东西的时候。路径为

>'/content/drive/My Drive/文件名称'

### 再用以下代码运行，进行转换

```python
import docx, os

START_FOLDER = "/content/drive/MyDrive/docx"
DEST_FOLDER = "/content/drive/MyDrive/TXT"

def docx2txt(filepath):
  file = docx.Document(filepath)
  txt_file_name = filepath.split("/")[-1].replace(".docx", ".txt")
  txt_path = "".join([DEST_FOLDER, '/', txt_file_name])
  print("段落数:"+str(len(file.paragraphs)))

  #输出每一段的内容
  with open(txt_path, 'wt', encoding='utf-8') as f:
    for para in file.paragraphs:
        f.write(para.text + '\n')
        # print(para.text)

files = os.listdir(START_FOLDER)
for file_docx in files:
  filepath = "".join([START_FOLDER, '/', file_docx])
  print(filepath)
  docx2txt(filepath)

print(len(files))
converted_files = os.listdir(DEST_FOLDER)
print(len(converted_files))
```
