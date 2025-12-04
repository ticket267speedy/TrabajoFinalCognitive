# TrabajoFinalCognitive

Sistema de asesoría y gestión de asistencia de estudiantes construido con Flask. Ofrece APIs y vistas autenticadas con JWT para dos roles (administrador y asesor), gestión de cursos y matrículas, alertas y un endpoint de salud. El repositorio incluye una versión simplificada en la raíz (sin funciones de IA) y una variante más completa en `TrabajoFinalCognitive1/` que integra AWS Rekognition para flujos basados en imágenes.

## Características Principales
- Autenticación con JWT (`/api/login`) y endpoints por rol
- Dashboard y perfil de administrador, gestión de cursos y estudiantes
- Dashboard del asesor, listas de becarios, gestión de alertas y resumen
- Migraciones de base de datos con Alembic/Flask-Migrate
- Soporte para MySQL (preferido) o SQLite vía `DATABASE_URL`
- Docker Compose para despliegue local rápido (proyecto raíz)

## Stack Tecnológico
- Backend: `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-JWT-Extended`, `Flask-CORS`
- Autenticación: tokens JWT Bearer
- Base de datos: MySQL 8 (por defecto en Docker) o SQLite
- Servidor: `gunicorn` para producción
- IA opcional (solo en `TrabajoFinalCognitive1/`): `boto3` con AWS Rekognition

## Estructura del Repositorio (proyecto raíz)
- `app/` — Aplicación Flask (factory, controladores, modelos, servicios, vistas)
- `migrations/` — Scripts de migración Alembic
- `run.py` — Punto de entrada del servidor de desarrollo
- `requirements.txt` — Dependencias de Python (sin IA)
- `.env` — Variables de entorno (URL de BD, secretos)
- `Dockerfile`, `docker-compose.yml` — Contenedores para la app y MySQL
- `update_db.py` — Script opcional para sembrar/restablecer datos de demo

El segundo proyecto está en `TrabajoFinalCognitive1/`, con estructura similar pero servicios de IA y recursos de OpenCV en `PROYECTO/`.

## Variables de Entorno
Defínelas en `.env` en la raíz del proyecto:
- `SECRET_KEY` — Llave secreta de Flask
- `JWT_SECRET_KEY` — Llave de firma JWT
- `DATABASE_URL` — Ejemplos: `mysql+pymysql://root:root@db:3306/proyecto_final` (Docker) o `mysql+pymysql://root:@localhost:3306/proyecto_final` (local)
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` — No usadas por la app raíz (IA deshabilitada); sí por `TrabajoFinalCognitive1/` si ejecutas esa variante.

Si falta `DATABASE_URL`, se usa por defecto `sqlite:///app.db`.

## Inicio Rápido (Docker)
Requisitos: Docker Desktop.

TrabajoFinalCognitive

Resumen
-------
TrabajoFinalCognitive es una aplicación backend construida con Flask para la gestión de asistencia académica y la administración de cursos. Provee APIs protegidas con JWT para dos roles principales (administrador y asesor), gestión de estudiantes y cursos, control de sesiones y un endpoint de salud.

Estructura de carpetas (resumen)
--------------------------------
- `app/`                    : Código principal de la aplicación (factory, blueprints, modelos, servicios, vistas)
- `migrations/`             : Scripts de migración de la base de datos (Alembic/Flask-Migrate)
- `run.py`                  : Punto de entrada para ejecutar la app en desarrollo
- `requirements.txt`        : Dependencias de Python
- `.env`                    : Variables de entorno (no versionar con Git)
- `docker-compose.yml`      : Configuración de Docker Compose (app + base de datos)
- `archived_docs/`          : Documentación antigua trasladada (no forma parte del README activo)

Funcionamiento básico
----------------------
1. Configurar variables de entorno en `.env` (ejemplo mínimo):

   SECRET_KEY=changeme
   JWT_SECRET_KEY=changeme
   DATABASE_URL="sqlite:///app.db"   # o URL a MySQL/Postgres

2. Entorno virtual e instalación de dependencias:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

3. Ejecutar migraciones (si aplica):

   flask db upgrade

4. Iniciar la aplicación en desarrollo:

   python run.py

   Por defecto la app escucha en `http://127.0.0.1:7000` o en la dirección configurada en las variables `HOST`/`PORT`.

Endpoints relevantes
--------------------
- `GET /health`                       : Health check, devuelve `{ "status": "ok" }`.
- `POST /api/chatbot`                 : Endpoint del chatbot (si está configurado con una API key válida en `.env`).
- `POST /api/login`                   : Autenticación y emisión de token JWT.
- Rutas de administrador bajo `/admin` : Panel y vistas del administrador.
- APIs bajo `/api`                    : Rutas REST para estudiantes, cursos, asistencia, etc.

Gestión del chatbot
--------------------
- La integración con proveedores de IA se configura mediante variables de entorno (por ejemplo `GOOGLE_API_KEY` para Google Gemini o `OPENAI_API_KEY` para OpenAI). No incluya claves en archivos `.md` ni en el repositorio.
- Si usa Gemini, instale `google-generativeai` y configure `GOOGLE_API_KEY` en `.env`.

Buenas prácticas
----------------
- No versionar archivos que contengan claves o secretos. Use `.env` y exclúyalo con `.gitignore`.
- Para producción, utilice un servidor WSGI (gunicorn, waitress, etc.) en lugar del servidor de desarrollo de Flask.
- Revise `archived_docs/` si necesita información histórica; todo lo útil ha sido consolidado en este `README.md`.

Comentarios finales
------------------
Este README está pensado como el documento principal para entender la estructura del proyecto y los pasos básicos para ejecutar y probar la aplicación localmente. Si desea que agregue secciones más detalladas (por ejemplo: despliegue en Docker, configuración avanzada del chatbot, o endpoints API documentados con ejemplos), indíquelo y lo añado.

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `app/templates/layout.html` | ✨ Nuevo (base template con estructura de SB Admin 2) |
| `app/views/admin/admin_dashboard.html` | ♻️ Refactorizado (ahora extiende `layout.html`) |
| `app/static/` | ➕ Assets de SB Admin 2 (vendor, css, js, img) |

### Archivos Sin Cambios

- `app/controllers/admin_controller.py` — Rutas y lógica backend intactas
- `app/controllers/api.py` — Endpoints de API sin modificar
- `app/models/`, `app/services/`, `app/repositories/` — Datos y lógica de negocio sin cambios
- Todas las funcionalidades REST y de autenticación se mantienen

### Cómo Usar la Nueva Estructura

#### Para extender el dashboard con nuevas páginas admin:

1. Crea una nueva plantilla en `app/views/admin/`:
```html
{% extends "layout.html" %}

{% block title %}Mi Nueva Página - CogniPass{% endblock %}

{% block content %}
<h1>Contenido de mi página</h1>
<div class="card shadow mb-4">
    <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-primary">Mi Sección</h6>
    </div>
    <div class="card-body">
        <!-- Tu contenido aquí -->
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Tu lógica JavaScript aquí
</script>
{% endblock %}
```

2. Declara la ruta en `app/controllers/admin_controller.py`:
```python
@admin_bp.get("/mi-pagina")
def mi_nueva_pagina():
    return render_template("admin/mi_nueva_pagina.html")
```

#### Para personalizar la sidebar:

Edita `app/templates/layout.html` en la sección de navegación (busca `<!-- Nav Item - ...`).

### Ventajas de la Migración

✅ Interfaz visual moderna y profesional  
✅ Sistema responsive (móvil, tablet, desktop)  
✅ Componentes Bootstrap 4 reutilizables  
✅ Menú sidebar colapsible para optimizar espacio  
✅ Topbar integrada con información del usuario  
✅ Mantenimiento de toda la funcionalidad anterior  
✅ Facilita agregar nuevas páginas admin en el futuro  

---
