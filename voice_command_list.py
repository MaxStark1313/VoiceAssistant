import tkinter as tk
import speech_recognition as sr
import ctypes
import io
import os
import pystray
import re
import sys
import subprocess
import threading
import time
from pywinauto import Application, Desktop
from PIL import Image, ImageDraw

# Настройка кодировки вывода для Python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Получение текущего рабочего каталога
current_directory = os.getcwd()

# Список программ и соответствующие команды для их запуска
programs = {
    ##Cmd
    "командную строку от имени администратора": os.path.join(current_directory, 'VBS_files', 'run_admin_cmd.vbs'),
    "сmd а ты меня администратора": os.path.join(current_directory, 'VBS_files', 'run_admin_cmd.vbs'),
    "сmd от имени администратора": os.path.join(current_directory, 'VBS_files', 'run_admin_cmd.vbs'),
    "cmd администратор": os.path.join(current_directory, 'VBS_files', 'run_admin_cmd.vbs'),
    "cmd administrator": os.path.join(current_directory, 'VBS_files', 'run_admin_cmd.vbs'),
    ##Another programs
    "калькулятор": r"C:\Windows\System32\calc.exe",
    "блокнот": r"C:\Windows\System32\notepad.exe",
    "discord": r"C:\Users\Acer\AppData\Local\Discord\app-1.0.9156\Discord.exe",
    "дискорд": r"C:\Users\Acer\AppData\Local\Discord\app-1.0.9156\Discord.exe",
    "чат gpt": os.path.join(current_directory, 'VBS_files', 'ChatGPT.vbs'),
    ##VS Code
    "Visual Studio code": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "Visual Studio": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "редактор кода": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "Verscode": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "Вес кот": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "Vescode": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "vs code": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "Vs Cold": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs'),
    "Rescold": os.path.join(current_directory, 'VBS_files', 'VSCode.vbs')
    #Folders
}

# Ключевые слова для распознавания команд
keywords = ["открыть", "запустить", "открой", "запусти", "открытие", "запуск",
            "open", "start", "launch", "run"]

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
    words = command.lower().split()

    # Определяем программы для запуска
    programs_to_run = []
    
    # Ищем ключевые слова и названия программ
    for word in words:
        if any(keyword in word for keyword in keywords):
            for program in programs:
                if program.lower() in command.lower():
                    programs_to_run.append(programs[program])

    # Запускаем все найденные программы
    for program in programs_to_run:
        run_program(program)
        text_var.set(f"Запуск: {', '.join([k for k, v in programs.items() if v in programs_to_run])}")


# Глобальные переменные для хранения текста и времени
recognized_text = ""
last_speech_time = time.time()
timeout_duration = 2  # Время в секундах для ожидания молчания

# Функция для распознавания речи
def recognize_speech(recognizer, microphone):
    global recognized_text, last_speech_time
    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language="ru-RU")
                print(f"Распознанный текст: {text}")
                
                # Обновление времени последней речи
                last_speech_time = time.time()
                
                # Обновление текста
                text_var.set(text)
                
                # Выполнение команды
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

# Функция для проверки молчания и очистки текста
def check_silence():
    global last_speech_time, recognized_text
    current_time = time.time()
    if current_time - last_speech_time > timeout_duration:
        # Если прошло больше времени, чем таймаут, очищаем текст
        text_var.set("")
    root.after(4000, check_silence)  # Проверять каждые 4 секунды

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

# Функция для создания иконки в системном трее
def create_tray_icon():
    # Загрузка изображения для иконки трея
    icon_image = Image.open(os.path.join("items", "icon_tray.png"))

    # Определяем действия для иконки трея
    def on_quit(icon, item):
        icon.stop()

    # Создаем иконку
    icon = pystray.Icon("name", icon_image, "Voice Assistant")
    icon.menu = pystray.Menu(pystray.MenuItem("Quit", on_quit))
    icon.run()

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
label = tk.Label(root, textvariable=text_var, font=("Verdana", 8))
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

# Запускаем проверку молчания
root.after(5000, check_silence)  # Начать проверку через 5 секунд

# Запуск иконки в системном трее
tray_thread = threading.Thread(target=create_tray_icon)
tray_thread.daemon = True
tray_thread.start()

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