import pychrome
import keyboard
import os
import pyautogui
import re
import shutil
import subprocess
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
        time.sleep(0)

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
        # Проверяем наличие кнопки stop-button
        stop_button_script = """
        (function() {
            var stopButton = document.querySelector('[data-testid="stop-button"]');
            return stopButton === null;
        })();
        """
        stop_button_result = tab.call_method("Runtime.evaluate", expression=stop_button_script)
        stop_button_not_found = stop_button_result.get('result', {}).get('value', False)
        
        if stop_button_not_found:
            # Если кнопка stop-button не найдена, проверяем наличие кнопки "Продолжить создание"
            continue_creation_button_script = """
            (function() {
                var continueButton = document.querySelector('button.btn.btn-secondary');
                return continueButton === null;
            })();
            """
            continue_creation_result = tab.call_method("Runtime.evaluate", expression=continue_creation_button_script)
            continue_creation_button_not_found = continue_creation_result.get('result', {}).get('value', False)
            
            if not continue_creation_button_not_found:
                # Кнопка "Продолжить создание" найдена, нажимаем её
                click_continue_button_script = """
                (function() {
                    var continueButton = document.querySelector('button.btn.btn-secondary');
                    if (continueButton) {
                        continueButton.click();
                        return true;
                    }
                    return false;
                })();
                """
                tab.call_method("Runtime.evaluate", expression=click_continue_button_script)
                
                # Ждем 1 секунду после клика на кнопку
                time.sleep(1)
            else:
                # Обе кнопки не найдены, считаем работу завершенной
                break
        else:
            # Кнопка stop-button еще есть, ждем 1 секунду
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

def replace_code_in_text(text_file_path, code_file_paths):
    # Чтение содержимого исходного текстового файла
    with open(text_file_path, 'r', encoding='utf-8') as text_file:
        text_content = text_file.read()

    # Обработка каждого файла с кодом
    for code_file_path in code_file_paths:
        with open(code_file_path, 'r', encoding='utf-8') as code_file:
            code_content = code_file.read()
        
        # Замена всех вхождений текста из code_file_path в text_content
        replacement_text = f'\nКод программы находится по пути "{code_file_path}".\n'
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

def process_code_files(code_file_paths):
    extensions = {
        "python": ".py",
        "csharp": ".cs",
        "cpp": ".cpp",
        "c": ".c",
        "java": ".java",
        "javascript": ".js",
        "ruby": ".rb",
        "php": ".php",
        "go": ".go",
        "swift": ".swift",
        "kotlin": ".kt",
        "rust": ".rs",
        "perl": ".pl",
        "r": ".R",
        "scala": ".scala"
    }
    
    processed_files = []
    for code_file_path in code_file_paths:
        with open(code_file_path, 'r', encoding='utf-8') as code_file:
            lines = code_file.readlines()
        
        # Извлечение первой строки для определения языка программирования и удаления лишнего текста
        first_line = lines[0]
        code_language = None
        for lang, ext in extensions.items():
            if first_line.lower().startswith(lang):
                code_language = lang
                extension = ext
                break

        if code_language:
            # Убираем название языка и "Копировать код"
            first_line = re.sub(rf"{code_language}Копировать код", "", first_line, flags=re.IGNORECASE).strip()
            
            # Записываем обработанные строки в новый файл
            output_dir = r"D:\Program_Data\Python\output_files"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            new_code_filename = f"{os.path.basename(code_file_path).replace('.code', extension)}"  # Заменяем .code на соответствующее расширение
            new_code_filepath = os.path.join(output_dir, new_code_filename)
            processed_files.append(new_code_filepath)
            
            with open(new_code_filepath, 'w', encoding='utf-8') as new_code_file:
                new_code_file.write(first_line + "\n")
                new_code_file.writelines(lines[1:])  # Остальные строки записываем как есть

    return processed_files

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

def clear_directory(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении {file_path}: {e}")

def replace_file_content(file_path, content):
    temp_file_path = file_path + ".tmp"
    # Записываем данные в временный файл
    with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        temp_file.write(content)
    
    # Переименовываем временный файл в исходный файл
    os.replace(temp_file_path, file_path)

def check_and_handle_files_old(dir):
    tmp_dir = r"D:\Program_Data\Python\voice_tmp"

    # Создаем директорию для сохранения файлов, если ее еще нет
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    tmp_voice_code_decision = os.path.join(tmp_dir, "tmp_voice_code_decision.txt")
    tmp_voice_code_answer = os.path.join(tmp_dir, "tmp_voice_code_answer.txt")

    # Проверка наличия файлов в папке output_files
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    if files:
        with open(tmp_voice_code_decision, 'w', encoding='utf-8') as decision_file:
            decision_file.write("В папке присутствуют сторонние файлы. Мне их удалить, перенести куда-то или показать?")
            print(f"Ожидается принятие решения с файлами в папке {dir}")

        while True:
            if os.path.exists(tmp_voice_code_answer):
                with open(tmp_voice_code_answer, 'r', encoding='utf-8') as answer_file:
                    answer = answer_file.read().strip()
                
                if answer == "Del":
                    for file in files:
                        os.remove(os.path.join(dir, file))
                    print(f"Файлы в папке {dir} были успешно удалены")
                    break
                
                elif answer.startswith("Move to: "):
                    target_dir = answer.split(": ")[1].strip()
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    for file in files:
                        src = os.path.join(dir, file)
                        dest = os.path.join(target_dir, file)
                        shutil.move(src, dest)
                        # Проверка существования файла в новой директории
                        if not os.path.exists(dest):
                            print(f"Не удалось перенести файл: {file}")
                        else:
                            print(f"Файл {file} из папки {dir} был успешно перенесён в папку {target_dir}")
                    break
                
                elif answer == "Show":
                    # Открыть все файлы в папке output_files
                    files_to_open = [os.path.join(dir, file) for file in files]
                    subprocess.run(["code"] + files_to_open, check=True)
                    print("Visual Studio Code открыта, ожидание дальнейших указаний...")
                    
                    while True:
                        if os.path.exists(tmp_voice_code_answer):
                            with open(tmp_voice_code_answer, 'r', encoding='utf-8') as answer_file:
                                answer = answer_file.read().strip()
                            
                            if answer in ["Del", "Move to:"]:
                                if answer == "Del":
                                    for file in files:
                                        os.remove(os.path.join(dir, file))
                                    print(f"Файлы в папке {dir} были успешно удалены")
                                elif answer.startswith("Move to:"):
                                    target_dir = answer.split(":")[1].strip()
                                    if not os.path.exists(target_dir):
                                        os.makedirs(target_dir)
                                    for file in files:
                                        src = os.path.join(dir, file)
                                        dest = os.path.join(target_dir, file)
                                        shutil.move(src, dest)
                                        if not os.path.exists(dest):
                                            print(f"Не удалось перенести файл: {file}")
                                        else:
                                            print(f"Файл {file} из папки {dir} был успешно перенесён в папку {target_dir}")
                                break
                            elif answer == "Show":
                                # Очистить файл и заново открыть VS Code
                                open(tmp_voice_code_answer, 'w').close()
                                files_to_open = [os.path.join(dir, file) for file in files]
                                subprocess.run(["code"] + files_to_open, check=True)
                                print("Visual Studio Code открыта, ожидание дальнейших указаний...")
                                continue

                        time.sleep(0.5)
                    
                    # Перезаписать файл tmp_voice_code_decision
                    with open(tmp_voice_code_decision, 'w', encoding='utf-8') as decision_file:
                        decision_file.write("Что мне делать со сторонними файлами?")
                    print(f"Ожидается принятие решения с файлами в папке {dir}")
    else:
        print(f"В папке {dir} нет файлов для обработки")

def check_and_handle_files(dir):
    tmp_dir = r"D:\Program_Data\Python\voice_tmp"
    tmp_voice_code_decision = os.path.join(tmp_dir, "tmp_voice_code_decision.txt")
    tmp_voice_code_answer = os.path.join(tmp_dir, "tmp_voice_code_answer.txt")
    
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    
    if files:
        with open(tmp_voice_code_decision, 'w', encoding='utf-8') as decision_file:
            decision_file.write("В папке присутствуют сторонние файлы. Мне их удалить, перенести куда-то или показать?")
            print(f"Ожидается принятие решения с файлами в папке {dir}")
        
        while True:
            if os.path.exists(tmp_voice_code_answer):
                with open(tmp_voice_code_answer, 'r', encoding='utf-8') as answer_file:
                    answer = answer_file.read().strip()
                
                if answer == "Del":
                    for file in files:
                        os.remove(os.path.join(dir, file))
                    print(f"Файлы в папке {dir} были успешно удалены")
                    break
                
                elif answer.startswith("Move to:"):
                    target_dir = answer.split(":")[1].strip()
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    for file in files:
                        src = os.path.join(dir, file)
                        dest = os.path.join(target_dir, file)
                        shutil.move(src, dest)
                        if not os.path.exists(dest):
                            print(f"Не удалось перенести файл: {file}")
                        else:
                            print(f"Файл {file} из папки {dir} был успешно перенесён в папку {target_dir}")
                    break
                
                elif answer == "Show":
                    files_to_open = [os.path.join(dir, file) for file in files]
                    subprocess.run(["code"] + files_to_open, check=True)
                    print("Visual Studio Code открыта, ожидание дальнейших указаний...")
                    
                    # Ожидание закрытия VS Code или обновления файла tmp_voice_code_answer.txt
                    while True:
                        time.sleep(2)
                        if os.path.exists(tmp_voice_code_answer):
                            with open(tmp_voice_code_answer, 'r', encoding='utf-8') as answer_file:
                                new_answer = answer_file.read().strip()
                            
                            if new_answer == "Del":
                                os.remove(tmp_voice_code_answer)
                                for file in files:
                                    os.remove(os.path.join(dir, file))
                                print(f"Файлы в папке {dir} были успешно удалены")
                                break
                            
                            elif new_answer.startswith("Move to: "):
                                os.remove(tmp_voice_code_answer)
                                target_dir = new_answer.split(": ")[1].strip()
                                if not os.path.exists(target_dir):
                                    os.makedirs(target_dir)
                                for file in files:
                                    src = os.path.join(dir, file)
                                    dest = os.path.join(target_dir, file)
                                    shutil.move(src, dest)
                                    if not os.path.exists(dest):
                                        print(f"Не удалось перенести файл: {file}")
                                    else:
                                        print(f"Файл {file} из папки {dir} был успешно перенесён в папку {target_dir}")
                                break
                            
                    
                    break
            
            time.sleep(1)
#                           elif new_answer == "Show":
#                               os.remove(tmp_voice_code_answer)
#                               # Повторное открытие VS Code
#                               subprocess.run(["code", dir], check=True)
#                               print("Visual Studio Code открыта, ожидание дальнейших указаний...")

def main():
    prompt = "Добавь в программу на языке java функцию вычисления тангенса"
    tmp_dir = r"D:\Program_Data\Python\tmp"
    output_dir = r"D:\Program_Data\Python\output_files"
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
        send_message(chatgpt_tab, prompt) # Пример отправки запроса и получения ответа

        # Ожидание получения ответа
        wait_for_response(chatgpt_tab)
        html_content = get_last_message_html(chatgpt_tab)

    finally:
        unblock_input()

    codes, text = extract_code_blocks(html_content)
    text_file_path, code_file_paths = save_to_file([text], codes)
    check_and_handle_files(output_dir)
    new_file_path = replace_code_in_text(text_file_path, code_file_paths)
    processed_code_files = process_code_files(code_file_paths)

    print(f"Обновленный текст сохранен в: {new_file_path}")
    print(f"Обработанные файлы с кодом сохранены в: {processed_code_files}")

    clear_directory(tmp_dir)
    print(f"Папка {tmp_dir} успешно очищена")

        

if __name__ == "__main__":
    main()