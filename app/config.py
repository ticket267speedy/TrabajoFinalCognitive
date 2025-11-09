import os
from dotenv import load_dotenv


# Carga variables desde .env
load_dotenv()


class Config:
    """Configuración base de la aplicación.

    Lee las variables de entorno necesarias para el funcionamiento del sistema,
    incluyendo seguridad, conexión a base de datos y credenciales AWS.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")

    # SQLAlchemy / MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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