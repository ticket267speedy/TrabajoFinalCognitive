import os
import time
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except Exception as e:
    logger.error('google-generativeai no está instalado o no se puede importar: %s', e)
    raise

API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise SystemExit('Necesitas definir GOOGLE_API_KEY en el entorno')

genai.configure(api_key=API_KEY)
MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

system_prompt = (
    "Eres el asistente de CogniPass. Responde en español, de forma breve (1-2 frases). "
    "Si la pregunta no está relacionada con CogniPass, responde: 'Solo puedo ayudarte con CogniPass. ¿Tienes dudas sobre asistencia, sesiones de clase o gestión de becarios?'"
)

few_shot = [
    {"author": "user", "content": "Responde solo: OK"},
    {"author": "assistant", "content": "OK"},
    {"author": "user", "content": "¿Cómo agrego un estudiante al curso?"},
    {"author": "assistant", "content": "Ve a 'Cursos', selecciona el curso, pulsa 'Agregar estudiante' y completa nombre y email. Guarda los cambios."},
    {"author": "user", "content": "¿Qué hago si la cámara no reconoce a un estudiante?"},
    {"author": "assistant", "content": "Marca asistencia manual desde la sesión y sube una foto de referencia si es recurrente."},
]

user_message = os.getenv('TEST_MESSAGE', '¿Cómo agrego un estudiante al curso?')

messages = [
    {"author": "system", "content": system_prompt},
] + few_shot + [
    {"author": "user", "content": user_message},
]

print('Enviando mensaje a Gemini:', user_message)
resp = genai.chat.create(model=MODEL, messages=messages, temperature=0.2, max_output_tokens=300)

print('\n--- RAW RESPONSE ---')
print(repr(resp))

# Intentar extraer texto
bot_response = None
try:
    if hasattr(resp, 'text') and resp.text:
        bot_response = resp.text.strip()
    elif hasattr(resp, 'candidates') and resp.candidates:
        try:
            bot_response = resp.candidates[0].content[0].text.strip()
        except Exception:
            try:
                bot_response = resp.candidates[0].message.get('content','').strip()
            except Exception:
                bot_response = None
    elif hasattr(resp, 'output') and resp.output:
        try:
            bot_response = resp.output[0].content[0].text.strip()
        except Exception:
            bot_response = None
    elif isinstance(resp, dict) and resp.get('candidates'):
        try:
            bot_response = resp['candidates'][0]['content'][0]['text'].strip()
        except Exception:
            bot_response = None
except Exception as ex:
    logger.debug('Error extrayendo texto: %s', ex)

print('\n--- EXTRACTED TEXT ---')
print(bot_response or '<NO RESPONSE EXTRACTED>')

# Guardar en log local
try:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
    log_dir = os.path.join(base, 'instance')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'gemini_raw_responses.log')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    with open(log_path, 'a', encoding='utf-8') as fh:
        fh.write(f"[{timestamp}] USER: {user_message}\nRESPONSE: {repr(resp)}\n\n")
    print('\nResponse logged to', log_path)
except Exception as e:
    print('No se pudo escribir log:', e)
