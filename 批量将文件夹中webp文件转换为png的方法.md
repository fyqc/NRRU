```cmd
for %i in (*.webp) do ffmpeg -i "%i" "%~ni.png"
```

NOTE:  
If you want to put this into a batch file on Windows 10, you need to use %%i.
