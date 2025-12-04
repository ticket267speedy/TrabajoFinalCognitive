"""
Script de prueba para verificar conexión con Google Gemini
Ejecutar: python test_gemini.py
"""
import os

# Puedes poner tu key aquí para probar, o usar variable de entorno
API_KEY = os.getenv('GOOGLE_API_KEY') or "AIzaSyAOiNkqT6jTxZ7ss1Xl4Fm_gMLpMIVYhpQ"

print(f"🔑 API Key: {API_KEY[:15]}...")
print("\n🧪 Probando conexión con Google Gemini...\n")

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Falta instalar el SDK de Google. Ejecuta:")
    print("   pip install google-generativeai")
    exit(1)

# Configurar la API
genai.configure(api_key=API_KEY)

# Modelos a probar (del más recomendado al menos)
MODELS = [
    "gemini-1.5-flash",      # Rápido, gratuito, recomendado
    "gemini-1.5-pro",        # Más capaz, también gratuito con límites
    "gemini-2.0-flash",      # Más nuevo (puede no estar disponible)
]

print("📋 Modelos disponibles en tu cuenta:")
try:
    for m in genai.list_models():
        # Dependiendo de la versión del SDK, la propiedad puede variar
        supported = getattr(m, 'supported_generation_methods', None)
        if supported and 'generateContent' in supported:
            print(f"   - {m.name}")
except Exception as e:
    print(f"   ⚠️ No se pudieron listar: {e}")

print("\n🧪 Probando modelos...\n")

for model_name in MODELS:
    try:
        print(f"  Probando: {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        # Dependiendo de la versión del SDK, la API puede variar ligeramente
        response = model.generate_content("Responde solo: OK")
        # Extraer texto de la respuesta de forma segura
        text = getattr(response, 'text', None) or getattr(response, 'candidates', [None])[0]
        if hasattr(text, 'strip'):
            text = text.strip()
        print(f"✅ Funciona! Respuesta: {text}")
        print(f"\n🎉 Modelo recomendado: {model_name}")
        print(f"\n✅ ¡Todo listo! Tu chatbot debería funcionar correctamente.")
        break
    except Exception as e:
        error = str(e)
        if "API_KEY_INVALID" in error or "invalid" in error.lower():
            print(f"❌ API Key inválida")
            print(f"\n⚠️ Genera una nueva key en: https://aistudio.google.com/apikey")
            break
        elif "not found" in error.lower() or "404" in error:
            print(f"⚠️ Modelo no disponible")
        else:
            print(f"❌ Error: {error[:200]}")
else:
    print("\n❌ Ningún modelo funcionó. Verifica tu API key.")
