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
        self.system_prompt = """Eres el asistente virtual de CogniPass, una plataforma de control de asistencia con reconocimiento facial.

=== CONTEXTO IMPORTANTE ===
El usuario es un ASESOR DE BECAS - una AUTORIDAD que supervisa y monitorea a los estudiantes becados.
NO es un alumno. Es un supervisor/gestor de becas que toma decisiones basadas en asistencia.

=== PLATAFORMA COGNIPASS ===
Sistema de control de asistencia de estudiantes becados con reconocimiento facial.

ROLES Y RESPONSABILIDADES:
• PROFESOR: Crea cursos, registra estudiantes, inicia sesiones de clase (cámara), marca asistencia manual
• ASESOR DE BECAS (Supervisor): MONITOREA becarios, SUPERVISA asistencia, RECIBE ALERTAS, TOMA ACCIONES

INFORMACIÓN QUE EL ASESOR SUPERVISA:
• Inasistencias totales de becarios
• Tardanzas (llegadas fuera de hora)
• Retiros anticipados (abandonos antes del final)
• Alertas automáticas por faltas injustificadas
• Historial de comportamiento en asistencia

FLUJO DE TRABAJO PARA EL ASESOR:
1. Accede al Dashboard
2. Ve lista de becarios asignados
3. Monitorea alertas de inasistencias/tardanzas/retiros
4. Toma decisiones sobre sanciones o seguimiento
5. Genera reportes de monitoreo

=== INSTRUCCIONES DE COMPORTAMIENTO ===
1. Dirígete al usuario como un SUPERVISOR/ASESOR, NO como alumno
2. Responde sobre CogniPass y monitoreo de asistencia de becarios
3. Solo menciona: inasistencias, tardanzas, retiros, alertas
4. Usa lenguaje de autoridad (sugerencias, acciones, supervisión)
5. Sé conciso: máximo 2-3 oraciones
6. Siempre en español
7. Asume que el usuario está tomando decisiones sobre becarios

=== EJEMPLO DE RESPUESTAS ===
❌ MAL: "Si tienes más de 3 faltas, se generará una alerta para tu asesor"
✅ BIEN: "Como asesor, recibirás una alerta cuando un becario acumule más de 3 inasistencias injustificadas"

=== PREGUNTAS FUERA DE TEMA ===
Si preguntan sobre temas no relacionados (recetas, matemáticas, películas, etc.):
Respuesta: "Mi función es asistirte con CogniPass. ¿Necesitas ayuda con monitoreo de becarios, alertas de asistencia o gestión de inasistencias?"

Sé amable pero mantén el enfoque. Si saludan, responde normalmente."""

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