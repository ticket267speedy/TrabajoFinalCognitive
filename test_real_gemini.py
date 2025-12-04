import os

print("=" * 50)
print("🧪 TEST REAL DE CONEXIÓN A GEMINI")
print("=" * 50)

# 1. Verificar que la librería está instalada
try:
    import google.generativeai as genai
    print("✅ google-generativeai está instalado")
except ImportError:
    print("❌ FALTA INSTALAR: pip install google-generativeai")
    print("\nEjecuta este comando y vuelve a probar:")
    print("   pip install google-generativeai")
    exit(1)

# 2. Verificar API key
API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    # Si no tienes API key en env, puedes ponerla aquí (NO RECOMENDADO en repositorios públicos)
    API_KEY = 'AIzaSyCerO8B17taVzW3iT_FhXnDTYDQgTXLCLI'  # fallback proporcionado por el usuario

print(f"✅ API Key: {API_KEY[:15]}... (oculto)")

# 3. Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"❌ Error configurando genai: {e}")
    exit(1)

# 4. Probar modelo
MODEL_NAME = 'gemini-2.0-flash'
print(f"\n📡 Conectando a {MODEL_NAME}...")

try:
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction="Eres el asistente de CogniPass. Responde en español, breve."
    )
    
    # Test simple
    response = model.generate_content("Di solo: CONEXIÓN OK")
    
    if getattr(response, 'text', None):
        print(f"✅ CONEXIÓN EXITOSA!")
        print(f"   Respuesta: {response.text.strip()}")
    else:
        print("⚠️ Respuesta vacía")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nPosibles causas:")
    print("1. API key inválida - genera una nueva en https://aistudio.google.com/apikey")
    print("2. Sin conexión a internet")
    print("3. Modelo no disponible")
    exit(1)

# 5. Test completo del chatbot
print("\n" + "=" * 50)
print("🤖 TEST DEL CHATBOT")
print("=" * 50)

preguntas = [
    ("Hola", "Saludo"),
    ("¿Cómo agrego un estudiante?", "Pregunta válida"),
    ("¿Cuál es la capital de Francia?", "Debe rechazar"),
]

for pregunta, tipo in preguntas:
    print(f"\n❓ [{tipo}] {pregunta}")
    try:
        resp = model.generate_content(pregunta)
        print(f"💬 {getattr(resp, 'text', '')[:150]}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ TEST COMPLETADO")
print("=" * 50)
print("\nSi todo funcionó, tu chatbot debería funcionar en la web.")
print("Reinicia Flask: flask run")
