document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const userInput = document.getElementById('user-input');
    const messageContainer = document.getElementById('messages');

    // Crear y mostrar el mensaje del usuario
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = userInput.value;
    messageContainer.appendChild(userMessage);

    // Enviar el mensaje al backend
    fetch('http://localhost:5005/webhooks/rest/webhook', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Incluye el CSRF token para seguridad
        },
        body: JSON.stringify({ message: userInput.value })
    })
    .then(response => response.json())
    .then(data => {
        // Crear y mostrar la respuesta del chatbot
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.textContent = data[0].text; // Asegúrate de que 'response' sea el nombre del campo con la respuesta en el JSON del backend
        messageContainer.appendChild(botMessage);

        // Desplazar hacia abajo para mostrar el último mensaje
        messageContainer.scrollTop = messageContainer.scrollHeight;
    })
    .catch(error => {
        console.error('Error al enviar el mensaje:', error);
    });

    userInput.value = '';
    messageContainer.scrollTop = messageContainer.scrollHeight; // Desplazar hacia abajo
});
// Función para obtener el token CSRF desde las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Si esta cookie comienza con el nombre buscado, devolver su valor
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}