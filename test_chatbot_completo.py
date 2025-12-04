"""
TEST COMPLETO DEL CHATBOT DE COGNIPASS
Prueba diferentes tipos de preguntas para ver cómo reacciona

Ejecutar: python test_chatbot_completo.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🧪 TEST COMPLETO DEL CHATBOT DE COGNIPASS")
print("=" * 60)

# Verificar librería
try:
    import google.generativeai as genai
except ImportError:
    print("❌ Instala: pip install google-generativeai")
    exit(1)

# API Key
API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    print("❌ GOOGLE_API_KEY no encontrada en .env")
    exit(1)

print(f"✅ API Key: {API_KEY[:15]}...")

# Configurar
genai.configure(api_key=API_KEY)

# System prompt balanceado
SYSTEM_PROMPT = """Eres el asistente virtual de CogniPass.

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

=== CÓMO COMPORTARTE ===
1. Responde preguntas sobre CogniPass con detalle útil
2. Sé amable y breve (2-3 oraciones)
3. Siempre en español

=== QUÉ HACER CON PREGUNTAS FUERA DE TEMA ===
Si preguntan algo NO relacionado con CogniPass (recetas, capitales, matemáticas, películas, etc.):
Responde: "Mi especialidad es ayudarte con CogniPass. ¿Tienes alguna duda sobre la plataforma?"

Si saludan, responde el saludo normalmente."""

# Crear modelo
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    system_instruction=SYSTEM_PROMPT
)

print(f"✅ Modelo: gemini-2.0-flash")

# ============================================================
# CASOS DE PRUEBA
# ============================================================

test_cases = [
    # === SALUDOS (debe responder normalmente) ===
    ("Hola", "SALUDO", "✅ Debe saludar"),
    ("Buenos días", "SALUDO", "✅ Debe saludar"),
    ("Qué tal?", "SALUDO", "✅ Debe saludar"),
    
    # === PREGUNTAS VÁLIDAS SOBRE COGNIPASS (debe responder) ===
    ("¿Cómo agrego un estudiante?", "COGNIPASS", "✅ Debe explicar"),
    ("¿Qué hago si la cámara no reconoce a un alumno?", "COGNIPASS", "✅ Debe explicar asistencia manual"),
    ("¿Cómo inicio una sesión de clase?", "COGNIPASS", "✅ Debe explicar"),
    ("¿Para qué sirve el dashboard?", "COGNIPASS", "✅ Debe explicar"),
    ("Soy asesor, ¿cómo veo las alertas?", "COGNIPASS", "✅ Debe explicar alertas"),
    ("¿Cómo funciona el reconocimiento facial?", "COGNIPASS", "✅ Debe explicar"),
    ("No puedo iniciar sesión", "COGNIPASS", "✅ Debe ayudar con login"),
    
    # === PREGUNTAS FUERA DE TEMA (debe rechazar amablemente) ===
    ("¿Cuál es la capital de Francia?", "OFF-TOPIC", "❌ Debe rechazar"),
    ("Dame una receta de pasta", "OFF-TOPIC", "❌ Debe rechazar"),
    ("¿Quién ganó el mundial 2022?", "OFF-TOPIC", "❌ Debe rechazar"),
    ("Cuéntame un chiste", "OFF-TOPIC", "❌ Debe rechazar"),
    ("¿Cómo programo en Python?", "OFF-TOPIC", "❌ Debe rechazar"),
    ("Escribe un poema", "OFF-TOPIC", "❌ Debe rechazar"),
    ("¿Cuánto es 25 x 48?", "OFF-TOPIC", "❌ Debe rechazar"),
    ("Recomiéndame una película", "OFF-TOPIC", "❌ Debe rechazar"),
    
    # === CASOS LÍMITE (podría responder o rechazar) ===
    ("¿Qué es reconocimiento facial?", "LÍMITE", "⚠️ Podría explicar en contexto de CogniPass"),
    ("¿Cómo funciona una cámara web?", "LÍMITE", "⚠️ Podría conectar con CogniPass"),
]

# ============================================================
# EJECUTAR TESTS
# ============================================================

print("\n" + "=" * 60)
print("🔬 EJECUTANDO PRUEBAS")
print("=" * 60)

results = {"pass": 0, "fail": 0, "unclear": 0}

for pregunta, categoria, esperado in test_cases:
    print(f"\n{'─' * 60}")
    print(f"📝 Categoría: {categoria}")
    print(f"❓ Pregunta: {pregunta}")
    print(f"📋 Esperado: {esperado}")
    
    try:
        response = model.generate_content(pregunta)
        respuesta = response.text.strip() if response.text else "(sin respuesta)"
        print(f"💬 Respuesta: {respuesta[:200]}")
        
        # Evaluar resultado
        respuesta_lower = respuesta.lower()
        
        if categoria == "OFF-TOPIC":
            # Debe mencionar CogniPass o rechazar
            if "cognipass" in respuesta_lower or "plataforma" in respuesta_lower or "especialidad" in respuesta_lower:
                print("✅ CORRECTO: Rechazó apropiadamente")
                results["pass"] += 1
            else:
                print("⚠️ ATENCIÓN: Respondió en lugar de rechazar")
                results["fail"] += 1
                
        elif categoria in ("SALUDO", "COGNIPASS"):
            # Debe dar respuesta útil
            if len(respuesta) > 10:
                print("✅ CORRECTO: Respondió")
                results["pass"] += 1
            else:
                print("⚠️ ATENCIÓN: Respuesta muy corta")
                results["unclear"] += 1
                
        else:  # LÍMITE
            print("⚠️ CASO LÍMITE: Revisar manualmente")
            results["unclear"] += 1
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results["fail"] += 1

# ============================================================
# RESUMEN
# ============================================================

print("\n" + "=" * 60)
print("📊 RESUMEN DE RESULTADOS")
print("=" * 60)
print(f"✅ Pasaron: {results['pass']}")
print(f"❌ Fallaron: {results['fail']}")
print(f"⚠️ Revisar: {results['unclear']}")
print(f"📈 Total: {sum(results.values())}")

if results['fail'] == 0:
    print("\n🎉 ¡Todas las pruebas críticas pasaron!")
else:
    print(f"\n⚠️ Hay {results['fail']} casos que necesitan ajuste en el system prompt")

print("\n" + "=" * 60)
print("💡 NOTAS:")
print("- Si muchos OFF-TOPIC fallan, hacer el system prompt más estricto")
print("- Si rechaza preguntas válidas, hacer el prompt menos estricto")
print("- Ajusta el system prompt en gpt_service.py según resultados")
print("=" * 60)
