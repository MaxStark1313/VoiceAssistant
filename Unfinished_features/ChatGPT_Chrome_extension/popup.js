document.getElementById('send').addEventListener('click', () => {
    const message = document.getElementById('message').value;
    chrome.runtime.sendMessage({ text: message });
  });