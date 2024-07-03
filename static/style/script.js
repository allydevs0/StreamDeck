// Função para enviar a ação para o servidor Flask
function sendAction(action) {
    fetch('/action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ button: action, app: document.getElementById('app_name').value })
    })
        .then(response => response.json())
        .then(data => {
            showMessage(data.message);
        })
        .catch(error => console.error('Error:', error));
}

// Função para atualizar o volume
function updateVolume(volume) {
    fetch('/action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ button: 'volume', level: volume, app: document.getElementById('app_name').value })
    })
        .then(response => response.json())
        .then(data => {
            showMessage(data.message);
        })
        .catch(error => console.error('Error:', error));
}

// Função para exibir mensagens
function showMessage(message) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = message;
    messageElement.classList.add('show');

    // Adiciona um timer para esconder a mensagem após 2 segundos
    setTimeout(() => {
        messageElement.classList.add('hide');
        setTimeout(() => {
            messageElement.classList.remove('show');
            messageElement.classList.remove('hide');
        }, 500); // tempo de animação de fade-out
    }, 2000);
}
