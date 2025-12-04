# 📚 CogniPass - Sistema de Gestión Académica y Asistencia
## Resumen Ejecutivo del Proyecto

---

## 🎯 Propósito General

**CogniPass** es un sistema web full-stack de gestión académica construido con **Flask** que permite:
- **Administradores (Profesores)**: Gestionar cursos, estudiantes, asistencia y alertas
- **Asesores**: Ver becarios asignados, revisar alertas y dashboards de estudiantes
- **Autenticación por roles** usando JWT tokens
- **Base de datos relacional** con PostgreSQL (Supabase) o MySQL

---

## 📁 Estructura del Proyecto

```
TrabajoFinalCognitive/
├── app/
│   ├── __init__.py              # Factory y registro de blueprints
│   ├── config.py                # Configuración (DB, JWT, secretos)
│   ├── extensions.py            # Inicialización de extensiones (db, jwt, cors)
│   │
│   ├── models/                  # Modelos SQLAlchemy (ORM)
│   │   ├── user.py              # Usuario (admin, asesor, estudiante)
│   │   ├── student.py           # Estudiante
│   │   ├── course.py            # Curso (dictado por admin)
│   │   ├── enrollment.py        # Matrícula estudiante-curso
│   │   ├── attendance.py        # Registro de asistencia
│   │   ├── alert.py             # Alerta de bajo rendimiento
│   │   ├── advisor_course_link.py  # Relación asesor-curso
│   │   └── __init__.py
│   │
│   ├── controllers/             # Rutas y lógica (MVC)
│   │   ├── admin_controller.py  # Rutas /admin, /api/admin (vistas + API)
│   │   ├── advisor_controller.py # Rutas /dashboard (vistas del asesor)
│   │   ├── shared_controller.py  # Rutas compartidas (login, landing)
│   │   ├── api.py               # API legacy (reconocimiento facial)
│   │   ├── assets_controller.py  # Archivos estáticos (KaiAdmin, Axis)
│   │   └── __init__.py
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── attendance_service.py # Cálculos y procesamiento de asistencia
│   │   ├── face_recognition_service.py # Integración de IA (facial)
│   │   ├── chatbot_service.py   # Servicio de chatbot
│   │   └── __init__.py
│   │
│   ├── repositories/            # Consultas de BD (Data Access Layer)
│   │   ├── attendance_repository.py
│   │   └── __init__.py
│   │
│   ├── static/                  # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   │   └── theme.css
│   │   ├── uploads/             # Fotos de perfil y documentos
│   │   └── vendor/              # Librerías externas (Bootstrap, etc.)
│   │
│   ├── views/                   # Templates Jinja2 (HTML)
│   │   ├── layout.html          # Layout base (SB Admin 2)
│   │   ├── admin/
│   │   │   ├── admin_dashboard.html
│   │   │   ├── admin_profile.html
│   │   │   ├── students.html
│   │   │   ├── students_create.html
│   │   │   ├── students_edit.html
│   │   │   ├── courses.html
│   │   │   ├── attendance.html
│   │   │   ├── attendance_create.html
│   │   │   ├── attendance_edit.html
│   │   │   ├── session_active.html
│   │   │   └── ...
│   │   ├── advisor/
│   │   │   ├── dashboard.html
│   │   │   └── ...
│   │   ├── shared/
│   │   │   ├── landing.html
│   │   │   ├── login.html
│   │   │   ├── course_people.html
│   │   │   └── ...
│   │   └── ...
│   │
│   └── tools/                   # Herramientas auxiliares
│       └── debug_sessions.py
│
├── migrations/                  # Scripts Alembic (versionamiento BD)
│   ├── alembic.ini
│   ├── env.py
│   ├── versions/
│   └── ...
│
├── run.py                       # Punto de entrada (servidor desarrollo)
├── update_db.py                 # Script para sembrar datos de demo
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno (NO comprometer)
├── docker-compose.yml           # Orquestación servicios (app + BD)
├── Dockerfile                   # Imagen Docker de la app
└── README.md                    # Documentación principal
```

---

## 🗄️ Modelos de Base de Datos (Relaciones)

```
User (admin, asesor, estudiante)
├── has many Courses (admin_id)
├── has many Enrollments (si es estudiante)
├── has many Alerts
├── has many AdvisorCourseLink (si es asesor)
└── has many StudentAttendances (si es estudiante)

Course (dictado por admin)
├── belongs to User (admin_id)
├── has many Enrollments
├── has many Attendance
├── has many Alerts
└── has many AdvisorCourseLink

Student
├── has many Enrollments
└── has many Attendance

Enrollment (matrícula estudiante-curso)
├── belongs to Student
└── belongs to Course

Attendance (asistencia estudiante en curso)
├── belongs to Student
└── belongs to Course

Alert (alerta de bajo rendimiento)
├── belongs to Student
├── belongs to Course
└── belongs to User (admin que creó)

AdvisorCourseLink (relación asesor-curso)
├── belongs to User (asesor)
└── belongs to Course
```

---

## 🔐 Autenticación y Autorización

### Flujo de Autenticación

1. **Login** (`POST /api/login`):
   - Usuario envía: `{ "email": "...", "password": "..." }`
   - Backend valida contra BD y genera `access_token` JWT
   - Cliente guarda token en `localStorage`

2. **Rutas Protegidas**:
   - Header: `Authorization: Bearer <access_token>`
   - Validado por `@jwt_required()` en Flask-JWT-Extended
   - Acceso basado en rol: `admin`, `asesor`, `estudiante`

3. **Tokens JWT**:
   - Algoritmo: HS256
   - Secreto: `JWT_SECRET_KEY` (.env)
   - Expirabilidad: configurable (por defecto sin expiración en dev)

---

## 🏗️ Arquitectura MVC

### **Models** (ORM SQLAlchemy)
- Definen esquema de BD y relaciones
- Archivo: `app/models/*.py`
- Métodos: `to_dict()`, `__repr__()`, etc.

### **Views** (Templates Jinja2)
- HTML + Bootstrap 4 / SB Admin 2
- Ubicación: `app/views/`
- Se usan: loops `{% for %}`, condicionales `{% if %}`, herencia `{% extends %}`

### **Controllers** (Blueprints Flask)
- Rutas GET/POST
- Lógica: validación, consultas BD, renderizado templates
- Ubicación: `app/controllers/`
- Nomenclatura: `admin_bp`, `advisor_bp`, etc.

---

## 📡 Endpoints Principales

### **COMPARTIDOS** (`shared_bp`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Landing page |
| GET | `/login` | Formulario login |
| POST | `/api/login` | Autenticación (genera JWT) |
| GET | `/register` | Formulario registro |
| POST | `/api/register` | Crear usuario |

### **ADMINISTRADOR** (`admin_bp` + `admin_api_bp`)

#### Vistas HTML
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/admin/` | Dashboard |
| GET | `/admin/profile` | Perfil del admin |
| GET | `/admin/students` | Lista de estudiantes |
| GET | `/admin/students/create` | Crear estudiante (formulario) |
| POST | `/admin/students/create` | Guardar estudiante |
| GET | `/admin/students/<id>/edit` | Editar estudiante |
| POST | `/admin/students/<id>/edit` | Guardar cambios |
| POST | `/admin/students/<id>/delete` | Eliminar estudiante |
| GET | `/admin/courses` | Lista de cursos |
| GET | `/admin/attendance` | Registro de asistencia |
| GET | `/admin/attendance/create` | Crear asistencia (formulario) |
| POST | `/admin/attendance/create` | Guardar asistencia |
| GET | `/admin/attendance/<id>/edit` | Editar asistencia |
| POST | `/admin/attendance/<id>/edit` | Guardar cambios |
| POST | `/admin/attendance/<id>/delete` | Eliminar asistencia |

#### APIs JSON
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/admin/profile` | Perfil autenticado (JWT) |
| PATCH | `/api/admin/profile` | Actualizar perfil |
| POST | `/api/admin/profile/photo` | Subir foto de perfil |
| GET | `/api/admin/students` | Lista de estudiantes (JSON) |
| POST | `/api/admin/students` | Crear estudiante (JSON) |
| GET | `/api/admin/courses` | Cursos del admin (JSON) |
| GET | `/api/admin/attendance` | Asistencia de todos los cursos (JSON) |

### **ASESOR** (`advisor_bp`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard/` | Dashboard del asesor |
| GET | `/dashboard/advisees` | Lista de becarios asignados |

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| **Lenguaje** | Python | 3.13+ |
| **Framework Web** | Flask | 2.x |
| **ORM** | SQLAlchemy | 2.x |
| **Base de Datos** | PostgreSQL / MySQL | 12+ / 8+ |
| **Autenticación** | Flask-JWT-Extended | 4.x |
| **CORS** | Flask-CORS | 4.x |
| **Migraciones** | Flask-Migrate / Alembic | 4.x |
| **Servidor** | Gunicorn | 20.x |
| **Seguridad** | passlib + bcrypt | - |
| **Frontend** | HTML5 + Bootstrap 4 | 4.6 |
| **JavaScript** | Vanilla JS + Fetch API | ES6+ |
| **Contenedores** | Docker & Docker Compose | Latest |

---

## ⚙️ Configuración (.env)

```env
# Flask
SECRET_KEY=tu_llave_secreta_aqui_cambiar_en_produccion

# JWT
JWT_SECRET_KEY=tu_llave_jwt_aqui_cambiar_en_produccion

# Base de Datos (REQUERIDA)
# PostgreSQL (Supabase)
DATABASE_URL=postgresql://user:password@host:port/database

# O MySQL
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/proyecto_final

# O SQLite (desarrollo)
# DATABASE_URL=sqlite:///app.db

# AWS (deshabilitado por defecto)
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_REGION=us-east-1
```

---

## 🚀 Cómo Ejecutar

### **Opción 1: Docker (Recomendado)**
```bash
docker compose up --build
# App en http://localhost:5000
# BD MySQL en localhost:3306
```

### **Opción 2: Local (Development)**
```bash
# 1. Crear venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o en Windows:
venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
# DATABASE_URL=mysql+pymysql://root:@localhost:3306/proyecto_final

# 4. Migraciones
flask db upgrade

# 5. (Opcional) Sembrar datos demo
python update_db.py

# 6. Ejecutar servidor
python run.py
# App en http://localhost:5000
```

---

## 🔄 Flujo de Trabajo Típico (Desarrollo)

1. **Crear feature branch**: `git checkout -b feature/nuevo-modulo`
2. **Hacer cambios**:
   - Agregar modelos en `app/models/`
   - Crear rutas en `app/controllers/`
   - Diseñar templates en `app/views/`
   - Escribir servicios en `app/services/`
3. **Si cambias BD**:
   - `flask db migrate -m "Descripción del cambio"`
   - `flask db upgrade`
4. **Probar**:
   - Vistas HTML: navegador `http://localhost:5000`
   - APIs: curl, Postman, o desde JS en consola
5. **Commit y push**:
   - `git add .`
   - `git commit -m "Descripción clara"`
   - `git push origin feature/nuevo-modulo`
6. **Pull Request**: En GitHub, mergeamos a `main`

---

## 📊 Casos de Uso Principales

### **Admin (Profesor)**
1. ✅ Ver dashboard con estadísticas (estudiantes, cursos, alertas)
2. ✅ Crear/Editar/Eliminar estudiantes
3. ✅ Crear/Editar/Eliminar cursos
4. ✅ Registrar asistencia manualmente o importar
5. ✅ Ver alertas de estudiantes con bajo rendimiento
6. ✅ Actualizar perfil (foto, descripción)

### **Asesor**
1. ✅ Ver dashboard personalizado
2. ✅ Listar estudiantes becarios asignados
3. ✅ Ver alertas de sus becarios
4. ✅ Revisar desempeño académico

### **Sistema**
1. ✅ Autenticación JWT segura
2. ✅ Migraciones automáticas de BD
3. ✅ Endpoint de salud (`/health`)
4. ✅ CORS configurado para APIs externas

---

## 🐛 Troubleshooting Común

| Problema | Solución |
|----------|----------|
| `DATABASE_URL no está configurada` | Agregar a `.env`: `DATABASE_URL=postgresql://...` |
| `No se conecta a la BD` | Verificar que servicio MySQL/PostgreSQL esté corriendo |
| `Error 401 en APIs` | Verificar token JWT en header `Authorization: Bearer ...` |
| `Template no encontrado` | Verificar ruta en `render_template()` vs carpeta `app/views/` |
| `Migraciones fallidas` | Ejecutar `flask db upgrade` después de cambios en modelos |

---

## 📝 Notas Adicionales

- **Branching Strategy**: Git Flow (`main` → `develop` → feature branches)
- **Convención de commits**: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- **Testing**: Usar `pytest` + `fixtures` para tests unitarios e integración
- **Logging**: Integrado con `print()` y `app.logger`; mejorable con `loguru`
- **Seguridad**: Habilitar `HTTPS` en producción, validar inputs, usar `.env`
- **Performance**: Implementar caché (Redis) y lazy loading en queries grandes

---

## 👥 Roles en el Sistema

| Rol | Acceso | Funcionalidades |
|-----|--------|-----------------|
| **admin** | `/admin/*` | CRUD completo de estudiantes, cursos, asistencia |
| **asesor** | `/dashboard/*` | Lectura de becarios, alertas, estadísticas |
| **estudiante** | Limitado | Ver su perfil, asistencia (futuro) |

---

## 📌 Resumen Técnico para IAGen/Comunicación

**Propósito**: Gestión académica integral con autenticación JWT.
**Tecnología**: Flask + SQLAlchemy + PostgreSQL/MySQL + Bootstrap 4.
**Estructura**: MVC clásico (Models, Views, Controllers) + Blueprints.
**Base de Datos**: Relacional con Alembic para migraciones.
**Seguridad**: JWT tokens, bcrypt para contraseñas.
**Frontend**: Templates Jinja2 + Vanilla JS (Fetch API).
**Despliegue**: Docker Compose o local con venv.

---

## 🔗 Enlaces de Referencia

- [Flask Official](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [Bootstrap 4](https://getbootstrap.com/docs/4.6/)
- [SB Admin 2 Theme](https://github.com/startbootstrap/startbootstrap-sb-admin-2)
- [Docker Compose](https://docs.docker.com/compose/)

---

**Última actualización**: Diciembre 2025  
**Rama activa**: `israel`  
**Estado**: En desarrollo (CRUD completo, módulos de asistencia y alertas implementados)
