"""
Servicio de Chatbot para CogniPass
Versión balanceada - restricciones suaves vía system prompt
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPTChatbotService:
    """Chatbot para CogniPass usando Google Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY no configurada en .env")
        
        self.provider = 'gemini'
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        # System prompt BALANCEADO
        self.system_prompt = """Eres el asistente virtual de CogniPass.

=== SOBRE COGNIPASS ===
Plataforma web para gestionar asistencia de estudiantes becados usando reconocimiento facial.

USUARIOS:
• PROFESOR: Crea cursos, agrega estudiantes, inicia sesiones (enciende cámara), marca asistencia manual.
• ASESOR DE BECAS: Ve becarios, recibe alertas de faltas, monitorea rendimiento.

FUNCIONES:
• Login con email/contraseña
• Dashboard con cursos y estadísticas
• Sesiones de clase (activar/desactivar cámara)
• Asistencia automática (facial) o manual
• Alertas para asesores

FLUJO:
1. Profesor inicia sesión → cámara activa
2. Estudiantes entran → detección facial automática
3. Si falla → asistencia manual
4. Profesor cierra sesión → cámara apagada

=== CÓMO COMPORTARTE ===
1. Responde preguntas sobre CogniPass con detalle útil
2. Sé amable y breve (2-3 oraciones máximo)
3. Siempre en español

=== QUÉ HACER CON PREGUNTAS FUERA DE TEMA ===
Si alguien pregunta algo que NO tiene relación con CogniPass, asistencia, educación o la plataforma:
- Ejemplos: recetas de cocina, capitales de países, matemáticas, películas, deportes, programación general, chistes, etc.
- Responde amablemente: "Mi especialidad es ayudarte con CogniPass. ¿Tienes alguna duda sobre la plataforma, asistencia o gestión de becarios?"

NO seas robótico. Si alguien saluda, responde el saludo normalmente."""

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt
        )
        
        logger.info(f"✅ Chatbot inicializado ({self.model_name})")

    def get_response(self, user_message: str, user_role: str = None) -> str:
        """Obtiene respuesta del chatbot."""
        
        if not user_message or not user_message.strip():
            return "¡Hola! Soy el asistente de CogniPass. ¿En qué puedo ayudarte?"

        try:
            prompt = user_message
            if user_role:
                role_lower = user_role.lower()
                if role_lower in ('admin', 'professor', 'profesor'):
                    prompt = f"[Usuario: Profesor] {user_message}"
                elif role_lower in ('advisor', 'asesor', 'client'):
                    prompt = f"[Usuario: Asesor] {user_message}"
            
            logger.info(f"📤 {user_message[:50]}...")
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return "No pude procesar tu pregunta. ¿Puedes reformularla?"
                
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"❌ Error: {e}")
            
            if "quota" in error_msg or "rate" in error_msg:
                return "Muchas solicitudes. Espera un momento."
            elif "blocked" in error_msg or "safety" in error_msg:
                return "No pude responder eso. ¿Puedo ayudarte con CogniPass?"
            else:
                return "Error procesando tu mensaje. Intenta de nuevo."


# Alias
ChatbotService = GPTChatbotService