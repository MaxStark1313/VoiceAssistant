import os
import sys
import io
import threading
import time
import tkinter as tk
import speech_recognition as sr
import VA_lib

# Настройка кодировки вывода для Python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Глобальные переменные
recognized_text = ""
last_speech_time = time.time()
timeout_duration = 2  # Время в секундах для ожидания молчания

# Функция для обновления времени последней речи
def update_last_speech_time():
    global last_speech_time
    last_speech_time = time.time()

# Список программ и соответствующие команды для их запуска
programs = {
    "командную строку от имени администратора": os.path.join(os.getcwd(), 'VBS_files', 'run_admin_cmd.vbs'),
    "сmd а ты меня администратора": os.path.join(os.getcwd(), 'VBS_files', 'run_admin_cmd.vbs'),
    "сmd от имени администратора": os.path.join(os.getcwd(), 'VBS_files', 'run_admin_cmd.vbs'),
    "cmd администратор": os.path.join(os.getcwd(), 'VBS_files', 'run_admin_cmd.vbs'),
    "cmd administrator": os.path.join(os.getcwd(), 'VBS_files', 'run_admin_cmd.vbs'),
    "калькулятор": r"C:\Windows\System32\calc.exe",
    "блокнот": r"C:\Windows\System32\notepad.exe",
    "discord": r"C:\Users\Acer\AppData\Local\Discord\app-1.0.9156\Discord.exe",
    "дискорд": r"C:\Users\Acer\AppData\Local\Discord\app-1.0.9156\Discord.exe",
    "чат gpt": os.path.join(os.getcwd(), 'VBS_files', 'ChatGPT.vbs'),
    "Visual Studio code": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "Visual Studio": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "редактор кода": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "Verscode": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "Вес кот": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "Vescode": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "vs code": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "Vs Cold": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs'),
    "Rescold": os.path.join(os.getcwd(), 'VBS_files', 'VSCode.vbs')
}

# Инициализация графического интерфейса
root = tk.Tk()
text_var = tk.StringVar()
text_var.set("Ожидание команды...")

label = VA_lib.init_gui(root, text_var)

# Создаем распознаватель и микрофон
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Запускаем распознавание речи в отдельном потоке
thread = threading.Thread(target=VA_lib.recognize_speech, args=(recognizer, microphone, text_var, VA_lib.execute_command, programs, update_last_speech_time))
thread.daemon = True
thread.start()

# Запускаем проверку молчания
root.after(5000, VA_lib.check_silence, root, text_var, last_speech_time, timeout_duration)  # Начать проверку через 5 секунд

# Запуск иконки в системном трее
tray_thread = threading.Thread(target=VA_lib.create_tray_icon)
tray_thread.daemon = True
tray_thread.start()

# Запуск графического интерфейса
root.mainloop()