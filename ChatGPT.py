import pychrome
import keyboard
import os
import re
import pyautogui
import subprocess
import threading
import time
from datetime import datetime
import win32com.client
from bs4 import BeautifulSoup

def activate_chrome_window(window_title):
    # Находим окно Chrome по заголовку
    # Важно: для этого нужен заголовок окна, который должен быть уникальным
    window = pyautogui.getWindowsWithTitle(window_title)
    
    if window:
        # Активируем окно
        window[0].maximize()
        window[0].activate()
        time.sleep(1)

def get_tab_url(tab):
    # Выполняем JavaScript для получения текущего URL
    result = tab.call_method("Runtime.evaluate", expression="window.location.href")
    return result.get('result', {}).get('value', '')

def activate_tab(tab):
    tab.call_method("Page.bringToFront")

def find_chatgpt_tab(browser):
    tabs = browser.list_tab()
    for tab in tabs:
        tab.start()  # Запускаем вкладку, чтобы она была готова для методов
        try:
            url = get_tab_url(tab)
            if "chatgpt.com" in url:
                return tab
        except Exception as e:
            print(f"Ошибка при получении URL: {e}")
    return None

def send_message(tab, message):
    # Выполняем JavaScript для отправки сообщения
    script = f"""
    (function() {{
        var input = document.querySelector('textarea'); // Найти текстовое поле
        if (input) {{
            input.focus(); // Установить фокус на поле ввода
            input.value = '{message}'; // Вставить текст
            var event = new Event('input', {{ bubbles: true }}); // Создать событие
            input.dispatchEvent(event); // Отправить событие

            var button = document.querySelector('[data-testid="send-button"]'); // Найти кнопку отправки
            if (button) {{
                button.focus(); // Установить фокус на кнопку отправки
                setTimeout(function() {{ button.click(); }}, 100); // Нажать кнопку с задержкой
            }} else {{
                console.log("Кнопка отправки не найдена.");
            }}
        }} else {{
            console.log("Поле ввода не найдено.");
        }}
    }})();
    """
    tab.call_method("Runtime.evaluate", expression=script)
    # Добавляем задержку в 1 секунду перед получением ответа
    time.sleep(1)

def wait_for_response(tab):
    while True:
        script = """
        (function() {
            var stopButton = document.querySelector('[data-testid="stop-button"]');
            return stopButton === null;
        })();
        """
        result = tab.call_method("Runtime.evaluate", expression=script)
        if result.get('result', {}).get('value', False):
            break
        time.sleep(1)

    # Добавляем задержку в 1 секунду перед получением ответа
    time.sleep(1)

def get_last_message_html(tab):
    # Выполняем JavaScript для получения текста последнего сообщения
    script = """
    (function() {
        var messages = document.querySelectorAll('.markdown.prose');
        if (messages.length > 0) {
            return messages[messages.length - 1].outerHTML;
        }
        return 'Сообщения не найдены';
    })();
    """
    result = tab.call_method("Runtime.evaluate", expression=script)
    return result.get('result', {}).get('value', '')

def extract_code_blocks(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    code_blocks = soup.find_all('pre')
    
    codes = [code_block.get_text() for code_block in code_blocks]
    text = soup.get_text()
    
    return codes, text

def save_to_file(texts, codes, max_files=10):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = r"D:\Program_Data\Python\tmp"
    # Создаем директорию для сохранения файлов, если ее еще нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Удаляем старые файлы, если их количество превышает max_files
    def delete_old_files(extension):
        files = [f for f in os.listdir(output_dir) if f.endswith(extension)]
        if len(files) > max_files:
            files.sort()
            for f in files[:len(files) - max_files]:
                os.remove(os.path.join(output_dir, f))

    delete_old_files('.txt')
    delete_old_files('.code')

    # Сохраняем текст
    text_filename = os.path.join(output_dir, f"tmp_output.txt")
    with open(text_filename, 'w', encoding='utf-8') as f:
        f.write(texts[0])  # Записываем только один текстовый файл

    # Сохраняем блоки кода
    for i, code in enumerate(codes, start=1):
        code_filename = os.path.join(output_dir, f"code_{current_time}_{i}.code")
        with open(code_filename, 'w', encoding='utf-8') as f:
            f.write(code)
    
    return text_filename, [os.path.join(output_dir, f"code_{current_time}_{i}.code") for i in range(1, len(codes) + 1)]

def replace_code_in_text_old(text_file_path, code_file_paths):

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = r"D:\Program_Data\Python\output_files"

    # Создаем директорию для сохранения файлов, если ее еще нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Читаем содержимое файлов
    with open(text_file_path, 'r', encoding='utf-8') as text_file:
        text_content = text_file.read()
    
    for code_file_path in code_file_paths:
        with open(code_file_path, 'r', encoding='utf-8') as code_file:
            code_content = code_file.read()
    
        code_pattern = re.escape(code_content)
        updated_text = re.sub(code_pattern, f'Код программы находится по пути "{code_file_path}".', text_content, flags=re.DOTALL)
        text_content = updated_text
    
    new_filename = f"out_text_{current_time}.txt"
    new_file_path = os.path.join(output_dir, new_filename)
    
    with open(new_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text_content)
    
    return new_file_path

def replace_code_in_text(text_file_path, code_file_paths):
    # Чтение содержимого исходного текстового файла
    with open(text_file_path, 'r', encoding='utf-8') as text_file:
        text_content = text_file.read()

    # Обработка каждого файла с кодом
    for code_file_path in code_file_paths:
        with open(code_file_path, 'r', encoding='utf-8') as code_file:
            code_content = code_file.read()
        
        # Замена всех вхождений текста из code_file_path в text_content
        replacement_text = f'Код программы находится по пути "{code_file_path}".'
        text_content = text_content.replace(code_content, replacement_text)
    
    # Генерация пути для нового файла
    output_dir = r"D:\Program_Data\Python\output_files"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    new_file_path = get_next_file_number(output_dir, prefix='out_text_', extension='.txt')
    
    # Запись обновленного текста в новый файл
    with open(new_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text_content)
    
    return new_file_path

# Пример функции get_next_file_number
def get_next_file_number(output_dir, prefix='out_text_', extension='.txt'):
    pattern = re.compile(rf'{re.escape(prefix)}\d+_{re.escape(extension)}$', re.IGNORECASE)
    files = [f for f in os.listdir(output_dir) if pattern.match(f)]
    max_number = 0
    for file in files:
        match = pattern.search(file)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
    next_number = max_number + 1
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_filename = f"{prefix}{current_time}_{next_number}{extension}"
    return os.path.join(output_dir, new_filename)

def run_devcon_command(command):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)

def get_device_by_id(device_id):
    wmi = win32com.client.GetObject("winmgmts:")
    devices = wmi.InstancesOf("Win32_PnPEntity")
    for device in devices:
        if device.PNPDeviceID.startswith(device_id):
            return device
    return None

def disable_mouse():
    try:
        run_devcon_command(r'devcon disable "HID\VID_09DA&PID_1A63&REV_000<&MI_01"')
        print(f"Device mouse bloody disabled")
    except subprocess.CalledProcessError as e:
        print(f"Error disabling device: {e.stderr}")

def enable_mouse():
    try:
        run_devcon_command(r'devcon enable "HID\VID_09DA&PID_1A63&REV_000<&MI_01"')
        print(f"Device mouse bloody enabled")
    except subprocess.CalledProcessError as e:
        print(f"Error enabling device: {e.stderr}")

def block_input():
    for i in range(150):
        keyboard.block_key(i)

    disable_mouse()

def unblock_input():
    for i in range(150):
        keyboard.unblock_key(i)
    
    enable_mouse()


def main():
    browser = pychrome.Browser(url="http://localhost:9222")    # Создаем клиент для подключения к браузеру
    activate_chrome_window("Google Chrome")                    # Замените "Google Chrome" на уникальный заголовок вашего окна
    block_input()                                              # Блокируем ввод
    

    try:
        # Попробуйте найти вкладку ChatGPT
        chatgpt_tab = find_chatgpt_tab(browser)
        if chatgpt_tab is None:
            print("Вкладка ChatGPT не найдена.")
            return
        else:
            print(f"Вкладка ChatGPT найдена: ID {chatgpt_tab}")

        activate_tab(chatgpt_tab)                              # Активируем вкладку
        send_message(chatgpt_tab, "Напиши функцию вычисления Арктангенса На языке Python") # Пример отправки запроса и получения ответа

        # Ожидание получения ответа
        wait_for_response(chatgpt_tab)
        html_content = get_last_message_html(chatgpt_tab)
        codes, text = extract_code_blocks(html_content)

        text_file_path, code_file_paths = save_to_file([text], codes)
        new_file_path = replace_code_in_text(text_file_path, code_file_paths)

        print(f"Обновленный текст сохранен в: {new_file_path}")

    finally:
        unblock_input()
        

if __name__ == "__main__":
    main()