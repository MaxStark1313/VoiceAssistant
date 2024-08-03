import pychrome
import keyboard
import os
import pyautogui
import subprocess
import threading
import time
from datetime import datetime
import win32com.client

def save_to_file(text, codes, max_files=10):
    now = datetime.now()
    max_files = 10  # Максимальное количество файлов в папке
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = "response_"
    directory = r"D:\Program_Data\Python\last_requests"

    if not os.path.exists(directory):
        os.makedirs(directory)

    files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.txt')]
    files.sort()
    if len(files) >= max_files:
        oldest_file = files[0]
        os.remove(os.path.join(directory, oldest_file))

    file_number = len(files) + 1
    filename = f"{base_filename}{file_number}_{date_str}.txt"
    filepath = os.path.join(directory, filename)

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(text)

    print(f"Ответ сохранен в файл: {filename}")