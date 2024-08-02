import pyautogui
import pychrome
import time

def activate_chrome_window(window_title):
    # Находим окно Chrome по заголовку
    # Важно: для этого нужен заголовок окна, который должен быть уникальным
    window = pyautogui.getWindowsWithTitle(window_title)
    
    if window:
        # Активируем окно
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

def get_last_message(tab):
    # Выполняем JavaScript для получения текста последнего сообщения
    script = """
    (function() {
        var messages = document.querySelectorAll('.markdown.prose');
        if (messages.length > 0) {
            return messages[messages.length - 1].innerText;
        }
        return 'Сообщения не найдены';
    })();
    """
    result = tab.call_method("Runtime.evaluate", expression=script)
    return result.get('result', {}).get('value', '')

def main():
    # Создаем клиент для подключения к браузеру
    browser = pychrome.Browser(url="http://localhost:9222")

    # Замените "ChatGPT" на уникальный заголовок вашего окна Chrome
    activate_chrome_window("Широтно-импульсная модуляция - Google Chrome")
    # Попробуйте найти вкладку ChatGPT
    chatgpt_tab = find_chatgpt_tab(browser)
    if chatgpt_tab is None:
        print("Вкладка ChatGPT не найдена.")
        return
    else:
        print(f"Вкладка ChatGPT найдена: ID {chatgpt_tab}")

    # Активируем вкладку
    activate_tab(chatgpt_tab)

    # Пример отправки запроса и получения ответа
    send_message(chatgpt_tab, "Что такое тип данных Void в языке C")

    # Ожидание, чтобы ChatGPT успел ответить
    wait_for_response(chatgpt_tab)

    response = get_last_message(chatgpt_tab)
    print(f"Ответ от ChatGPT: {response}")

if __name__ == "__main__":
    main()