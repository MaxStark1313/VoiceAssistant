import tkinter as tk
import speech_recognition as sr
import ctypes
import io
import os
import re
import sys
import subprocess
import threading
import time
from pywinauto import Application, Desktop

# Настройка кодировки вывода для Python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Список программ и соответствующие команды для их запуска
programs = {
    #Programs
    "калькулятор": r"C:\Windows\System32\calc.exe",
    "блокнот": r"C:\Windows\System32\notepad.exe",
    #"дискорд": r"C:\Users\Acer\AppData\Local\Discord\app-1.0.9156\Discord.exe",
    "дискорд": r"C:\Users\Acer\AppData\Local\Discord\app-1.0.9156\Discord.exe",
    "возможно": r"D:\Program_Data\Python\VBS_files\ChatGPT.vbs",
    #VS Code
    "Visual Studio code": r"D:\Program_Data\Python\VBS_files\VSCode.vbs",
    "Visual Studio": r"D:\Program_Data\Python\VBS_files\VSCode.vbs",
    "редактор кода": r"D:\Program_Data\Python\VBS_files\VSCode.vbs",
    "Verscode": r"D:\Program_Data\Python\VBS_files\VSCode.vbs",
    "Вес кот": r"D:\Program_Data\Python\VBS_files\VSCode.vbs",
    "Vescode": r"D:\Program_Data\Python\VBS_files\VSCode.vbs",
    "Vs Cold": r"D:\Program_Data\Python\VBS_files\VSCode.vbs",
    "Rescold": r"D:\Program_Data\Python\VBS_files\VSCode.vbs"
    #Folders

}

# Функция для запуска программы
def run_program(command):
    try:
        if command.endswith('.vbs'):
            # Используем cscript для запуска VBS файлов
            subprocess.Popen(['cscript', command])
        else:
            subprocess.Popen(command)
    except Exception as e:
        print(f"Ошибка запуска программы: {e}")

# Функция для открытия программ
def execute_command(command):
    keywords = ["Открыть", "Запустить", "Открой", "Запусти", "Открытие", "Запуск"]
    words = command.split()

    # Определяем программы для запуска
    programs_to_run = []
    
    for word in words:
        if word in keywords:
            for program in programs:
                if program in command:
                    programs_to_run.append(programs[program])
    # Запускаем все найденные программы
    for program in programs_to_run:
        run_program(program)
        text_var.set(f"Запуск: {', '.join([k for k, v in programs.items() if v in programs_to_run])}")


# Глобальная переменная для хранения текста
recognized_text = ""

# Функция для распознавания речи
def recognize_speech(recognizer, microphone):
    global recognized_text
    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, phrase_time_limit=5)
                text = recognizer.recognize_google(audio, language="ru-RU")
                print(f"Распознанный текст: {text}")
                recognized_text += " " + text  # Добавляем новое слово к уже распознанному тексту
                text_var.set(recognized_text.strip())
                execute_command(text.strip())
                
                # Обновляем размер окна в зависимости от размера текста
                label.update_idletasks()
                new_width = label.winfo_reqwidth() + 20  # Добавляем отступы
                new_height = label.winfo_reqheight() + 20  # Добавляем отступы
                root.geometry(f"{new_width}x{new_height}+{root.winfo_screenwidth() - new_width}+{root.winfo_screenheight() - new_height}")
        except sr.UnknownValueError:
            pass  # Ожидание следующего слова
        except sr.RequestError as e:
            print(f"Ошибка запроса к сервису Google Speech Recognition: {e}")
        except sr.WaitTimeoutError:
            pass # Таймаут при ожидании начала речи

# Функция для обновления текста в графическом окне
def update_text():
    command = recognize_speech()
    text_var.set(command)
    execute_command(command)  # Выполняем команду после распознавания

    # Обновляем размер окна в зависимости от размера текста
    label.update_idletasks()
    new_width = label.winfo_reqwidth() + 20  # Добавляем отступы
    new_height = label.winfo_reqheight() + 20  # Добавляем отступы
    root.geometry(f"{new_width}x{new_height}+{root.winfo_screenwidth() - new_width}+{root.winfo_screenheight() - new_height}")

    root.after(10, update_text)  # Обновлять каждые 1 секунд

# Создание графического окна с tkinter
root = tk.Tk()
root.attributes('-transparentcolor', 'white')  # Установка прозрачного цвета
root.attributes('-topmost', True)  # Держит окно поверх всех других
root.overrideredirect(True)  # Удаляет заголовок окна

# Установка начальных размеров окна и цвета фона
root.geometry("400x100")
root.configure(bg='white')  # Цвет фона, который будет прозрачным

# Создание переменной для хранения текста
text_var = tk.StringVar()
text_var.set("Ожидание команды...")

# Создание метки для отображения текста
label = tk.Label(root, textvariable=text_var, font=("Verdana", 14))
label.pack(padx=10, pady=10)

# Установка прозрачности окна
hwnd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.SetWindowLongW(hwnd, -20, ctypes.windll.gdi32.SetBkMode(hwnd, 1))
ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 10, 200, 2)  # Устанавливаем прозрачность: 0-255 (0 полностью прозрачно, 255 непрозрачно)

# Создаем распознаватель и микрофон
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Запускаем распознавание речи в отдельном потоке
thread = threading.Thread(target=recognize_speech, args=(recognizer, microphone))
thread.daemon = True
thread.start()
# Запуск графического интерфейса
root.mainloop()

# # Подключение к уже запущенному Notepad
# app = Application().connect(title_re=".*Notepad")
# dlg = app.window(title_re=".*Notepad")

# # Распознавание команды
# command = recognize_speech()

# if command:
#     # Извлечение имени файла из команды
#     match = re.search(r'с именем (\S+)', command)
#     if match:
#         filename = match.group(1)

#         # Открытие диалогового окна "Save As"
#         dlg.menu_select("File->Save As")
#         save_as_dlg = Desktop(backend="uia").window(title="Save As", control_type="Window")
        
#         # Ввод имени файла
#         save_as_dlg.Edit.type_keys(filename)
#         save_as_dlg.Save.click()

#         # Подтверждение перезаписи файла, если необходимо
#         try:
#             overwrite_dlg = Desktop(backend="uia").window(title="Confirm Save As", control_type="Window")
#             overwrite_dlg.Yes.click()
#         except Exception as e:
#             print("Диалоговое окно подтверждения перезаписи не появилось")
#     else:
#         print("Не удалось найти имя файла в команде")