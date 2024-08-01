@echo off

set nircmd_path=C:\Windows\nircmd.exe

start "" "D:\Program_Files\ChatGPT\ChatGPT.exe"

REM Задержка, чтобы программа успела запуститься
timeout /t 2

nircmd.exe win move process "ChatGPT.exe" -1000 -1000 200 200
REM Установка окна на передний план
nircmd.exe win settopmost process "ChatGPT.exe" 1

REM Разворачивание окна в полноэкранный режим
nircmd.exe win max process "ChatGPT.exe"
