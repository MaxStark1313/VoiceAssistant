@echo off

set nircmd_path=C:\Windows\nircmd.exe

start "" "D:\Program_Files\Microsoft VS Code\Code.exe"

REM Задержка, чтобы программа успела запуститься
timeout /t 1

REM Разворачивание окна в полноэкранный режим
nircmd.exe win max process "Code.exe"

timeout /t 1