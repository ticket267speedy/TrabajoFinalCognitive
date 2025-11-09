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