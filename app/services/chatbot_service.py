from typing import Dict, Any

def get_chatbot_response(message: str) -> str:
    """
    Simple rule-based chatbot response generation.
    """
    message = message.lower().strip()
    
    rules = {
        "hola": "¡Hola! Soy el asistente virtual de CogniPass. ¿En qué puedo ayudarte?",
        "asistencia": "Para marcar asistencia, el profesor debe iniciar una sesión y tú debes mirar a la cámara cuando se solicite.",
        "asesor": "Tu asesor es el encargado de monitorear tu rendimiento. Puedes ver sus datos en tu perfil.",
        "falta": "Si tienes más de 3 faltas injustificadas, se generará una alerta para tu asesor.",
        "beca": "Recuerda que mantener tu beca depende de tu asistencia y rendimiento académico.",
        "adios": "¡Hasta luego! Que tengas un buen día.",
        "ayuda": "Puedo ayudarte con temas de asistencia, contacto con asesores y dudas sobre la beca."
    }
    
    for key, response in rules.items():
        if key in message:
            return response
            
    return "Lo siento, no entiendo tu pregunta. Intenta con palabras clave como 'asistencia', 'asesor' o 'ayuda'."
