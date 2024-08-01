@echo off
:: Создание временного файла PowerShell
set "psFile=%temp%\elevate.ps1"
echo Start-Process cmd -ArgumentList @('/k') -Verb RunAs > "%psFile%"

:: Запуск PowerShell для выполнения временного файла с правами администратора
powershell -ExecutionPolicy Bypass -File "%psFile%"

:: Удаление временного файла
del "%psFile%"