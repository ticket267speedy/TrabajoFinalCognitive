# CogniPass - Plataforma de Asistencia con Reconocimiento Facial

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev)

## Descripción

**CogniPass** es una plataforma web para gestionar asistencia de estudiantes becados utilizando reconocimiento facial automático. Permite a profesores registrar la asistencia de forma eficiente y a asesores de becas monitorear el rendimiento en tiempo real.

## Características Principales

- **Reconocimiento Facial Automático**: Detección y registro automático de asistencia usando cámara web
- **Panel de Profesor**: Crear cursos, gestionar estudiantes, iniciar sesiones de clase
- **Dashboard de Asesor**: Monitoreo de asistencia, alertas de faltas, reportes de becarios
- **Asistente IA (Chatbot Gemini)**: Soporte automático en español sobre la plataforma
- **Autenticación JWT**: Control de acceso seguro por rol (Profesor/Asesor)
- **Interfaz Responsiva**: Diseño adaptado para escritorio y móvil

## Stack Tecnológico

### Backend
- **Framework**: Flask (Python 3.10+)
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migraciones**: Alembic

### Frontend
- **Bootstrap 5**: Interfaz responsive
- **Chart.js**: Visualización de estadísticas
- **JavaScript Vanilla**: Interactividad

### IA
- **Google Gemini 2.0 Flash**: Modelo de lenguaje para chatbot
- **OpenCV**: Detección de rostros

## Instalación y Ejecución

### Requisitos Previos
- Python 3.10+
- PostgreSQL 12+
- pip / pip3
- Git

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/ticket267speedy/TrabajoFinalCognitive.git
cd TrabajoFinalCognitive
```

### Paso 2: Configurar Variables de Entorno

```bash
cp .env.example .env
```

Edita `.env` y configura:
```ini
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@host:5432/cognipass

# Seguridad
SECRET_KEY=tu_clave_secreta_aqui
JWT_SECRET_KEY=tu_jwt_secret_aqui

# Google Gemini (Chatbot)
GOOGLE_API_KEY=tu_api_key_google_aqui
GEMINI_MODEL=gemini-2.0-flash

# Flask
FLASK_ENV=development
FLASK_APP=run.py
PORT=7000
```

**Nota**: Obtén tu API Key de Google en: https://aistudio.google.com/app/apikey

### Paso 3: Crear Entorno Virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### Paso 4: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: Inicializar Base de Datos

```bash
flask db upgrade
```

### Paso 6: Ejecutar la Aplicación

```bash
python run.py
```

La aplicación estará disponible en: **http://127.0.0.1:7000**

## Uso

### Para Profesores
1. Login con credenciales de profesor
2. Crear o seleccionar un curso
3. Iniciar sesión de clase (activa cámara)
4. El sistema registra asistencia automáticamente
5. Si falla la cámara, marcar manualmente

### Para Asesores de Becas
1. Login con credenciales de asesor
2. Ver lista de becarios bajo supervisión
3. Monitorear alertas de faltas
4. Acceder a reportes detallados

### Chatbot IA
- Pregunta sobre funcionalidades de CogniPass
- Responde en español
- Rechaza preguntas fuera de tema amablemente

## Estructura del Proyecto

```
TrabajoFinalCognitive/
├── app/
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuración
│   ├── models/                  # Modelos de BD
│   │   ├── student.py
│   │   ├── course.py
│   │   ├── attendance.py
│   │   └── user.py
│   ├── controllers/             # Rutas y lógica
│   │   ├── admin_controller.py
│   │   ├── advisor_controller.py
│   │   └── api.py
│   ├── services/                # Servicios
│   │   ├── attendance_service.py
│   │   ├── face_recognition_service.py
│   │   └── chatbot_service.py
│   ├── ai/chatbot/              # Chatbot Gemini
│   │   ├── gpt_service.py       # Servicio IA
│   │   ├── faq_es.csv           # Base de FAQs
│   │   └── __init__.py
│   ├── views/                   # Templates HTML
│   ├── static/                  # CSS, JS, imágenes
│   └── repositories/            # Acceso a datos
├── migrations/                  # Migraciones DB (Alembic)
├── run.py                       # Punto de entrada
├── requirements.txt             # Dependencias
├── .env.example                 # Variables de entorno
├── docker-compose.yml           # Compose para Docker
├── Dockerfile                   # Container
└── README.md                    # Este archivo
```

## Sistema de Chatbot IA

El chatbot utiliza **Google Gemini 2.0 Flash** para proporcionar soporte automático:

### Funcionalidades
- Responde preguntas sobre CogniPass
- Guía en procesos de la plataforma
- Rechaza preguntas fuera de tema
- Responde siempre en español

### Configuración
El sistema prompt está en `app/ai/chatbot/gpt_service.py`

### FAQs
Las preguntas frecuentes se cargan desde `app/ai/chatbot/faq_es.csv`

## Configuración Avanzada

### Docker (Opcional)
```bash
docker-compose up -d
```

## Troubleshooting

### Error de conexión a BD
- Verifica que PostgreSQL esté corriendo
- Revisa `DATABASE_URL` en `.env`

### Chatbot no responde
- Verifica `GOOGLE_API_KEY` en `.env`
- Revisa que sea una API Key válida
- Verifica conexión a internet

### Reconocimiento facial no funciona
- Verifica permisos de cámara web
- Instala opencv-python: `pip install opencv-python`

## Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/login` | Autenticación de usuario |
| GET | `/api/admin/profile` | Perfil del profesor |
| GET | `/api/admin/metrics` | Métricas generales |
| POST | `/api/chatbot` | Consultar al chatbot IA |
| GET | `/api/advisor/alerts` | Alertas para asesor |

## Licencia

Este proyecto está bajo la licencia MIT.

## Autor

**Trabajo Final Cognitivev5** - Sistema de asistencia con IA

---

**Última actualización**: Diciembre 2025
