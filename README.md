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

1) Construir y levantar servicios:
```
docker compose up --build
```
2) App disponible en `http://localhost:5000/` y salud en `http://localhost:5000/health`.
3) En el primer arranque, las migraciones se ejecutan automáticamente dentro del contenedor (`flask db upgrade`).

Compose establece `DATABASE_URL` en `mysql+pymysql://root:root@db:3306/proyecto_final` y expone MySQL en `localhost:3306`.

## Inicio Rápido (Desarrollo Local)
Requisitos: Python 3.13, MySQL 8 (o SQLite) y un entorno virtual.

1) Crear y activar venv (Windows PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2) Instalar dependencias:
```
pip install -r requirements.txt
```
3) Configurar `.env`:
```
SECRET_KEY=changeme
JWT_SECRET_KEY=changeme
DATABASE_URL="mysql+pymysql://root:@localhost:3306/proyecto_final"
```
4) Crear BD y correr migraciones:
```
python -m flask db upgrade
```
5) (Opcional) Sembrar datos de demo:
```
python update_db.py
```
6) Ejecutar la app:
```
python run.py
```
La app escucha en `http://localhost:5000/`.

## Factory y Salud
- Factory: `app.create_app()` configura extensiones y registra blueprints.
- Salud: `GET /health` devuelve `{ "status": "ok" }`.

## Autenticación
- Vista: `GET /login` sirve la página de login.
- API: `POST /api/login` recibe JSON `{ "email": "...", "password": "..." }` y retorna `access_token` más datos del usuario. Usa `Authorization: Bearer <token>` para rutas protegidas.

## Endpoints de Administrador (`/admin`)
- Vistas:
  - `GET /admin/` — Dashboard de administrador
  - `GET /admin/profile` — Perfil del administrador
  - `GET /admin/course/<course_id>/session` — Vista de sesión activa por curso
- API:
  - `GET /admin/api/profile` — Perfil autenticado del admin (con cursos)
  - `PATCH /admin/api/profile` — Actualizar descripción
  - `POST /admin/api/profile/photo` — Subir foto de perfil (se guarda en `app/static/uploads`)
  - `GET /admin/api/students` — Listar estudiantes con filtro `scholarship=true|false`
  - `GET /admin/api/courses` — Cursos dictados por el admin con conteo de becarios

## Endpoints de Asesor (`/dashboard`)
- Vistas:
  - `GET /dashboard/` — Dashboard del asesor
- API:
  - `GET /dashboard/api/students` — Estudiantes becarios
  - `GET /dashboard/api/alerts` — Alertas ordenadas por fecha
  - `PATCH /dashboard/api/alerts/<id>/read` — Marcar alerta como leída
  - `GET /dashboard/api/summary` — Estadísticas (becarios, alertas, cursos)

## Endpoints Compartidos
- Vistas:
  - `GET /register`, `GET /forgot-password`
  - `GET /course/<course_id>/people` — Personas del curso (profesor + becarios)
- API:
  - `GET /api/users/<user_id>/profile` — Perfil público (requiere auth)
  - `GET /api/courses/<course_id>/people` — Profesor y becarios del curso

## Modelo de Datos (selección)
- `User`, `Course`, `Student`, `Enrollment`, `Alert`, `ClassSession`, `AttendanceSummary`, `AdvisorCourseLink` (ver `app/models/`)

## Variante: `TrabajoFinalCognitive1/`
- Incluye `app/services/rekognition_service.py` y referencias desde `app/controllers/api.py` para asistencia basada en imagen.
- Añade `boto3` en `requirements.txt` y recursos de OpenCV en `PROYECTO/`.
- Usa `.env` en esa carpeta para proveer credenciales AWS si ejecutas esta variante.

## Subida de Archivos
- Las fotos de perfil se guardan en `app/static/uploads/`.
- En Docker, esta ruta está montada para persistir archivos entre reinicios del contenedor.

## Solución de Problemas
- Errores de conexión a BD: valida que `DATABASE_URL` concuerde con tu entorno y que la BD esté accesible.
- Migraciones: si la estructura deriva, ejecuta `python -m flask db upgrade` (local) o reinicia los contenedores para re-ejecutar el comando.
- Errores de JWT: asegúrate de enviar el header `Authorization` y que el token no esté expirado.

## Licencia
Proyecto académico/educativo. No se provee licencia explícita.

---

## Migración a SB Admin 2 Bootstrap 4 (Reciente)

A partir de la versión actual, el dashboard del administrador ha sido refactorizado para utilizar el tema profesional **SB Admin 2** basado en Bootstrap 4. Esta migración mejora significativamente la apariencia visual y la experiencia de usuario.

### Cambios Principales

#### 1. **Nueva Estructura de Plantillas (Templates)**
- **`app/templates/layout.html`** — Plantilla base reutilizable que incluye:
  - Sidebar con navegación principal (Dashboard, Estudiantes, Cursos, Sesiones, Asistencia, Asesores)
  - Topbar responsive con información del usuario y dropdown
  - Footer con copyright
  - Scripts de Bootstrap 4 y jQuery
  - Bloques `{% block content %}` y `{% block extra_js %}` para extensión

- **`app/views/admin/admin_dashboard.html`** — Refactorizado para:
  - Extender `layout.html` con `{% extends "layout.html" %}`
  - Insertar el contenido dentro de `{% block content %}`
  - Mantener toda la lógica JavaScript y funcionalidad anterior intacta
  - Utilizar cards de Bootstrap 4 (`.card`, `.card-header`, `.card-body`) para secciones

#### 2. **Assets de SB Admin 2**
Se han copiado al proyecto los siguientes recursos de `startbootstrap-sb-admin-2-gh-pages`:
- `app/static/vendor/` — jQuery, Bootstrap 4, Font Awesome, Chart.js, DataTables, jQuery Easing
- `app/static/css/sb-admin-2.min.css` — Estilos del tema (170 KB)
- `app/static/js/sb-admin-2.min.js` — Scripts del tema
- `app/static/img/` — Iconografía SVG (perfiles, ilustraciones)

#### 3. **Preservación de Funcionalidad**
Todos los IDs, nombres de campos, listeners de eventos y lógica JavaScript del dashboard anterior se han conservado:
- Gestión de estudiantes (CRUD con paginación)
- Gestión de cursos (listado)
- Control de sesiones de clase (iniciar, finalizar, ver activa)
- Resumen de asistencia
- Invitación de asesores
- Modales de Bootstrap 5 para agregar/editar estudiantes
- Detección automática de prefijo API (`/api/admin` vs `/admin/api`)
- Autenticación JWT y redirección a login

#### 4. **Sistema de Rutas (url_for)**
Todas las rutas usan `url_for()` de Flask para mayor robustez:
- `{{ url_for('admin_bp.admin_dashboard_view') }}` → `/admin/`
- `{{ url_for('admin_bp.admin_profile_view') }}` → `/admin/profile`
- `{{ url_for('static', filename='...') }}` → Assets en `/static/`

#### 5. **Estructura HTML Mejorada**
El contenido del dashboard ahora se presenta en cards de Bootstrap 4:
```html
<div class="card shadow mb-4">
    <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-primary">
            <i class="fas fa-users"></i> Estudiantes
        </h6>
    </div>
    <div class="card-body">
        <!-- Contenido de la sección -->
    </div>
</div>
```

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
