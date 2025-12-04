/**
 * Chatbot Widget para CogniPass
 * Integración simple del asistente de chat en cualquier página
 */

(function() {
    'use strict';

    // Esperar a que el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        initializeChatbot();
    });

    function initializeChatbot() {
        const container = document.getElementById('chatbot-widget');
        
        if (!container) {
            console.warn('[Chatbot] No se encontró elemento #chatbot-widget');
            return;
        }

        // HTML del widget
        const html = `
            <div class="chatbot-container" style="display: flex; flex-direction: column; height: 400px; border: 1px solid #e0e0e0; border-radius: 8px; background: white;">
                <!-- Historial de mensajes -->
                <div id="chatbot-messages" style="flex: 1; overflow-y: auto; padding: 15px; background: #f9f9f9; border-bottom: 1px solid #e0e0e0;">
                    <div class="chatbot-message bot" style="margin-bottom: 10px; padding: 10px; background: #e3f2fd; border-radius: 6px; max-width: 80%; color: #333;">
                        <strong>CogniPass</strong>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">¡Hola! Soy el asistente de CogniPass. ¿En qué puedo ayudarte?</p>
                    </div>
                </div>

                <!-- Input de mensaje -->
                <div style="padding: 10px; display: flex; gap: 8px;">
                    <input id="chatbot-input" type="text" placeholder="Escribe tu pregunta..."
                           style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                    <button id="chatbot-send" class="btn btn-primary btn-sm" 
                            style="padding: 10px 15px; border-radius: 4px;">
                        Enviar
                    </button>
                </div>
                <div id="chatbot-error" style="padding: 5px 10px; color: #d32f2f; font-size: 12px; display: none;"></div>
            </div>
        `;

        container.innerHTML = html;

        // Elementos
        const messagesDiv = document.getElementById('chatbot-messages');
        const inputField = document.getElementById('chatbot-input');
        const sendBtn = document.getElementById('chatbot-send');
        const errorDiv = document.getElementById('chatbot-error');

        // Event listeners
        sendBtn.addEventListener('click', sendMessage);
        inputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        // Función para enviar mensaje
        async function sendMessage() {
            const message = inputField.value.trim();
            
            if (!message) return;

            // Mostrar mensaje del usuario
            addMessageToChat('user', message);
            inputField.value = '';
            errorDiv.style.display = 'none';

            try {
                // Enviar a API
                const token = localStorage.getItem('access_token');
                const headers = {
                    'Content-Type': 'application/json'
                };
                
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`;
                }

                const response = await fetch('/api/chatbot', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        message: message,
                        role: 'advisor'  // El usuario es un asesor
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Error al obtener respuesta');
                }

                // Mostrar respuesta del bot
                addMessageToChat('bot', data.response || data.message || 'Sin respuesta');

            } catch (error) {
                console.error('[Chatbot Error]', error);
                errorDiv.textContent = error.message || 'Error de conexión';
                errorDiv.style.display = 'block';
                addMessageToChat('bot', '❌ Error: ' + (error.message || 'No se pudo conectar con el servidor.'));
            }
        }

        // Función para agregar mensaje al chat
        function addMessageToChat(sender, text) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `chatbot-message ${sender}`;
            msgDiv.style.cssText = `
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 6px;
                max-width: 80%;
                font-size: 14px;
                word-wrap: break-word;
                ${sender === 'user' 
                    ? 'background: #c8e6c9; color: #1b5e20; align-self: flex-end; margin-left: auto;' 
                    : 'background: #e3f2fd; color: #333; align-self: flex-start;'
                }
            `;
            msgDiv.innerHTML = `
                <strong>${sender === 'user' ? 'Tú' : 'CogniPass'}:</strong>
                <p style="margin: 5px 0 0 0; white-space: pre-wrap;">${escapeHtml(text)}</p>
            `;
            
            messagesDiv.appendChild(msgDiv);
            // Auto-scroll al último mensaje
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Función para escapar HTML (seguridad)
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }
})();
