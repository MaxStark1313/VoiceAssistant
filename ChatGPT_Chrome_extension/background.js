const ws = new WebSocket('ws://localhost:8766');

ws.onmessage = async function(event) {
    console.log('Message from server: ', event.data);
    
    // Здесь добавьте код для отправки запроса в ChatGPT
    const result = await sendMessageToChatGPT(event.data);
    ws.send(result);  // Отправляем результат обратно через WebSocket
};

async function sendMessageToChatGPT(message) {
    // Здесь добавьте код для взаимодействия с ChatGPT через DOM или API
    // Пример:
    let result = '';
    // Найти поле ввода и кнопку отправки на странице ChatGPT
    const textarea = document.querySelector('textarea');
    const button = document.querySelector('[data-testid="send-button"]');
    if (textarea && button) {
      textarea.value = message;
      button.click();
      
      // Подождать, пока ответ не появится на странице
      // Реализуйте механизм ожидания ответа
      // Например, с использованием MutationObserver или другого подходящего метода
      result = 'Response from ChatGPT';  // Замените на реальный результат
    }
    return result;
}

ws.onopen = function() {
  console.log('WebSocket connection opened');
  isWebSocketOpen = true;  // Устанавливаем флаг, что соединение открыто
};

ws.onerror = function(error) {
  console.error('WebSocket error: ', error);
};

ws.onclose = function() {
  console.log('WebSocket connection closed');
  isWebSocketOpen = false;  // Сбрасываем флаг при закрытии соединения
};

// Функция для открытия страницы ChatGPT
function openChatGPT() {
    chrome.tabs.create({ url: 'https://chatgpt.com' });
}

function authenticate() {
  
    // Подождите, пока страница загрузится
    setTimeout(() => {
      // Найдите поля для ввода логина и пароля
      let emailInput = document.querySelector('input[type="email"]');
      let passwordInput = document.querySelector('input[type="password"]');
      let loginButton = document.querySelector('button[type="submit"]');
  
      if (emailInput && passwordInput && loginButton) {
        emailInput.value = 'your_email@example.com'; // Вставьте ваш логин
        passwordInput.value = 'your_password'; // Вставьте ваш пароль
  
        // Имитируем нажатие кнопки
        loginButton.click();
      } else {
        console.error('Не удалось найти элементы для ввода данных');
      }
    }, 5000); // Увеличьте задержку, если нужно больше времени для загрузки страницы
  }
  
  authenticate();
  
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'sendMessage') {
      chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, {action: 'sendMessage', message: request.message}, (response) => {
          console.log(response.status);
        });
      });
    }
    if (message.action === "authenticate") {
        authenticate();
    }
    if (message.action === "openChatGPT") {
        openChatGPT();
    }
  });  