"""
Script de diagnóstico para verificar conexión a Supabase.
Ejecuta con: python diagnose_db.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("📊 DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS")
print("=" * 60)

db_url = os.getenv("DATABASE_URL")
print(f"\n1️⃣  DATABASE_URL configurada: {bool(db_url)}")

if not db_url:
    print("   ❌ DATABASE_URL no está configurada en .env")
    exit(1)

print(f"   ✅ DATABASE_URL: {db_url[:50]}...")

# Detectar tipo de BD
if "sqlite" in db_url:
    print("   📦 Tipo: SQLite (Local)")
elif "postgresql" in db_url:
    print("   📦 Tipo: PostgreSQL (Supabase)")
    
    # Probar conexión a PostgreSQL
    print("\n2️⃣  Probando conexión a Supabase...")
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print("   ✅ Conexión a Supabase: EXITOSA")
    except Exception as e:
        print(f"   ❌ Conexión a Supabase: FALLIDA")
        print(f"   Error: {str(e)[:100]}")
        print("\n   💡 Soluciones posibles:")
        print("      - Verifica credenciales en DATABASE_URL")
        print("      - Verifica que tu IP esté en whitelist de Supabase")
        print("      - Verifica conectividad de red")
        print("      - Intenta con SQLite: DATABASE_URL=sqlite:///app.db")
        exit(1)

# Probar con SQLAlchemy
print("\n3️⃣  Probando con SQLAlchemy...")
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("   ✅ SQLAlchemy: EXITOSA")
except Exception as e:
    print(f"   ❌ SQLAlchemy: FALLIDA")
    print(f"   Error: {str(e)[:100]}")
    exit(1)

print("\n" + "=" * 60)
print("✅ TODAS LAS PRUEBAS PASARON - Base de datos lista")
print("=" * 60)
