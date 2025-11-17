from flask import Flask, jsonify

from .config import Config
from .extensions import db, migrate, jwt, cors
from .controllers.api import api_bp
from .controllers.admin_controller import admin_bp
from .controllers.advisor_controller import advisor_bp
from .controllers.shared_controller import shared_bp
from .controllers.assets_controller import kaiadmin_bp, axis_bp

from . import models

def create_app(config_class: type = Config) -> Flask:
    """App Factory para inicializar la aplicación Flask.

    - Carga configuración
    - Inicializa extensiones (db, migrate, jwt, cors)
    - Registra controladores MVC
    """
    app = Flask(__name__, template_folder='views', static_folder='static')
    app.config.from_object(config_class)

    # Inicialización de extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Endpoint de salud para ver si la aplicación esta corriendo
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # Diagnóstico: listar blueprints registrados
    @app.get("/_blueprints")
    def _blueprints():
        return jsonify(sorted(list(app.blueprints.keys())))

    # Registro de Blueprints (Controladores MVC)
    app.register_blueprint(shared_bp)  # Rutas compartidas (login, register, etc.)
    app.register_blueprint(admin_bp, url_prefix="/admin")  # Rutas del administrador
    app.register_blueprint(advisor_bp, url_prefix="/dashboard")  # Rutas del asesor
    app.register_blueprint(api_bp, url_prefix="/api")  # API legacy (reconocimiento facial)
    # Archivos estáticos adicionales (KaiAdmin y Axis)
    app.register_blueprint(kaiadmin_bp)
    app.register_blueprint(axis_bp)

    return app