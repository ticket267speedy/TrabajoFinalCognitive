import os
from dotenv import load_dotenv


# Carga variables desde .env
load_dotenv()


class Config:
    """Configuración base de la aplicación.

    Lee las variables de entorno necesarias para el funcionamiento del sistema.
    Usa PostgreSQL en Supabase como base de datos (producción).
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")

    # SQLAlchemy / PostgreSQL (Supabase)
    # REQUERIDO: DATABASE_URL debe estar en .env
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError(
            "❌ ERROR: DATABASE_URL no está configurada en .env\n"
            "Añade a .env:\n"
            "DATABASE_URL=postgresql://user:password@host:port/database"
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Opciones de conexión para PostgreSQL (Supabase)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    # AWS deshabilitado: sin integración de Rekognition ni IA
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None
    AWS_REGION = None

    # JWT (brinda los tokens)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_TYPE = "Bearer"

    # CORS (ajustable según endpoints)
    CORS_SUPPORTS_CREDENTIALS = True

    # Feature flags removidos: versión sin integración de reconocimiento facial