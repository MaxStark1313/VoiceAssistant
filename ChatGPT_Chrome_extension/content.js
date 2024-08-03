// Функция для выполнения авторизации на странице ChatGPT
function login() {
    let emailInput = document.querySelector('input[type="email"]');
    let passwordInput = document.querySelector('input[type="password"]');
    let loginButton = document.querySelector('button[type="submit"]');
    
    if (emailInput && passwordInput && loginButton) {
        emailInput.value = 'your-email@example.com'; // Замените на ваш email
        passwordInput.value = 'your-password'; // Замените на ваш пароль
        loginButton.click();
    } else {
        console.log('Не удалось найти элементы для входа.');
    }
}

// Функция для отправки сообщения
function sendMessage(message) {
    let textarea = document.querySelector('textarea');
    let button = document.querySelector('[data-testid="send-button"]');
  
    if (textarea && button) {
      textarea.value = message;
      button.click();
    } else {
      console.error('Не удалось найти элементы для отправки сообщения');
    }
}
  
  // Слушаем сообщения от расширения
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'sendMessage') {
        sendMessage(request.message);
        sendResponse({status: 'Message sent'});
    }
    if (message.action === "login") {
        login();
    }
});