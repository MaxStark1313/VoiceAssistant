from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os
import asyncio
import websockets
import json

MAX_FILES = 10  # Максимальное количество файлов в папке

async def send_message_to_ws(message):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            'action': 'sendMessage',
            'message': message
        }))

def send_message(driver, message):
    try:
        # Заполнение текстового поля
        script_fill_textarea = f"""
        (function() {{
            var textarea = document.querySelector('textarea#prompt-textarea');
            if (textarea) {{
                textarea.value = '{message}';
                textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }})();
        """
        driver.execute_script(script_fill_textarea)
        
        # Нажатие кнопки отправки
        script_click_button = """
        (function() {
            var button = document.querySelector('button[data-testid="send-button"]');
            if (button) {
                button.click();
            }
        })();
        """
        driver.execute_script(script_click_button)
        print("Message sent.")
    except Exception as e:
        print(f"Error sending message: {e}")

def wait_for_page_load(driver):
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea#prompt-textarea'))
    )
    print("Page loaded.")

def wait_for_response(driver):
    try:
        # Ожидание кнопки с data-testid="stop-button"
        stop_button_xpath = '//*[@data-testid="stop-button"]'
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, stop_button_xpath)))
        print("Stop button found.")
    except TimeoutException:
        print("Timeout: Stop button not found.")

def get_last_message(driver):
    response_elements = driver.find_elements(By.CSS_SELECTOR, '.markdown.prose')
    response = response_elements[-1].text if response_elements else 'Сообщения не найдены'
    return response

def save_to_file(text):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = "response_"
    directory = "last_requests"

    if not os.path.exists(directory):
        os.makedirs(directory)

    files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.txt')]
    files.sort()
    if len(files) >= MAX_FILES:
        oldest_file = files[0]
        os.remove(os.path.join(directory, oldest_file))

    file_number = len(files) + 1
    filename = f"{base_filename}{file_number}_{date_str}.txt"
    filepath = os.path.join(directory, filename)

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(text)

    print(f"Ответ сохранен в файл: {filename}")

def main():
    # Пример вызова
    asyncio.get_event_loop().run_until_complete(send_message_to_ws("Давай создадим программу на языке Python, которая будет сохранять текст в файлы в папке 'last_requests'."))

if __name__ == "__main__":
    main()
