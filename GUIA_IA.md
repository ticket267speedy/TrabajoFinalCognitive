# 🤖 Guía de Comunicación con IAs para Desarrollo del Proyecto

Esta guía permite a otras IAs entender rápidamente la estructura y contexto del proyecto **CogniPass**.

---

## 1️⃣ Información Básica para Compartir

### Resumen de Una Línea
> **CogniPass**: Sistema Flask de gestión académica con autenticación JWT, gestión de cursos/estudiantes y registro de asistencia. Diseñado para profesores (admin) y asesores.

### Tecnología Stack
- **Backend**: Flask + SQLAlchemy (Python 3.13+)
- **BD**: PostgreSQL/MySQL + Alembic (migraciones)
- **Frontend**: Jinja2 + Bootstrap 4 + Vanilla JS (Fetch API)
- **Auth**: JWT Bearer tokens
- **Deployment**: Docker Compose + Gunicorn

### Rama Activa
- **Repo**: `ticket267speedy/TrabajoFinalCognitive`
- **Branch**: `israel`
- **Estado**: Desarrollo activo

---

## 2️⃣ Preguntas Típicas que IAs Deben Resolver

### 🎯 "¿Cómo agrego una nueva funcionalidad?"

**Pasos sistemáticos**:

1. **Modelo (ORM)**
   - Archivo: `app/models/nuevo_modelo.py`
   - Hereda: `db.Model`
   - Ejemplo:
   ```python
   from app.extensions import db
   from datetime import datetime
   
   class MiModelo(db.Model):
       __tablename__ = 'mi_modelo'
       
       id = db.Column(db.Integer, primary_key=True)
       nombre = db.Column(db.String(150), nullable=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       
       def to_dict(self):
           return {"id": self.id, "nombre": self.nombre}
   ```

2. **Migración de BD**
   ```bash
   flask db migrate -m "Add MiModelo table"
   flask db upgrade
   ```

3. **Controller (Rutas)**
   - Archivo: `app/controllers/admin_controller.py` (si es admin)
   - Crear funciones con decoradores:
   ```python
   @admin_bp.get("/mi-ruta")
   def mi_vista():
       return render_template("admin/mi_template.html")
   
   @admin_api_bp.get("/admin/mi-endpoint")
   @jwt_required()
   def mi_api():
       return jsonify({"data": "..."})
   ```

4. **Template (HTML)**
   - Archivo: `app/views/admin/mi_template.html`
   - Hereda: `{% extends "layout.html" %}`
   - Usa Bootstrap 4 + SB Admin 2

5. **Lógica de negocio** (opcional)
   - Archivo: `app/services/mi_servicio.py`
   - Métodos puros sin I/O directo

6. **Test** (si existe test suite)
   - Archivo: `tests/test_mi_modelo.py`

---

### 🔧 "¿Cómo modifico un modelo existente?"

1. Editar `app/models/archivo.py`
2. Crear migración: `flask db migrate -m "Update Model"`
3. Revisar script en `migrations/versions/XXXXX.py`
4. Ejecutar: `flask db upgrade`
5. Testear cambios

**IMPORTANTE**: Nunca edites BD directamente sin migración.

---

### 🔐 "¿Cómo protejo una ruta?"

```python
from flask_jwt_extended import jwt_required

# Opción 1: Decorador JWT
@admin_bp.get("/admin/privado")
@jwt_required()
def ruta_privada():
    return "Solo autenticado"

# Opción 2: Obtener user_id del token
@admin_api_bp.get("/admin/mis-datos")
@jwt_required()
def mis_datos():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"user": user.to_dict()})
```

---

### 📊 "¿Cómo consulto la BD?"

```python
# Consultas básicas
from app.models import Student, Course

# Obtener uno
estudiante = Student.query.get(1)
estudiante = Student.query.filter_by(email="test@test.com").first()

# Obtener todos
todos = Student.query.all()

# Con filtros complejos
from sqlalchemy import and_, or_
resultados = Student.query.filter(
    and_(
        Student.first_name.contains("Juan"),
        Student.is_scholarship_student == True
    )
).all()

# Contar
cantidad = Student.query.count()

# Ordenar y paginar
pagina = Student.query.order_by(Student.created_at.desc()).limit(10).offset(0).all()

# Con relaciones (eager loading)
from sqlalchemy.orm import joinedload
cursos = Course.query.options(joinedload(Course.enrollments)).all()
```

---

### 🎨 "¿Cómo creo una vista HTML?"

1. Crear archivo: `app/views/admin/nueva_vista.html`
2. Extender layout:
```html
{% extends "layout.html" %}

{% block title %}Título - CogniPass{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Page Heading -->
    <div class="d-sm-flex align-items-center justify-content-between mb-4">
        <h1 class="h3 mb-0 text-gray-800">Mi Vista</h1>
        <a href="#" class="d-none d-sm-inline-block btn btn-sm btn-primary shadow-sm">
            <i class="fas fa-plus fa-sm text-white-50 mr-2"></i>Agregar
        </a>
    </div>

    <!-- Card de contenido -->
    <div class="card shadow mb-4">
        <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Contenido</h6>
        </div>
        <div class="card-body">
            <!-- Tu contenido aquí -->
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// Tu JavaScript aquí
</script>
{% endblock %}
```

3. En controller:
```python
@admin_bp.get("/mi-vista")
def mi_vista():
    datos = Model.query.all()
    return render_template("admin/nueva_vista.html", datos=datos)
```

---

### 📡 "¿Cómo creo un endpoint de API?"

```python
from flask import jsonify, request
from flask_jwt_extended import jwt_required

@admin_api_bp.get("/admin/datos")
@jwt_required()
def obtener_datos():
    """GET /api/admin/datos - Obtener datos"""
    try:
        datos = Model.query.all()
        return jsonify({"data": [d.to_dict() for d in datos]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_api_bp.post("/admin/datos")
@jwt_required()
def crear_dato():
    """POST /api/admin/datos - Crear dato"""
    try:
        data = request.get_json()
        nuevo = Model(nombre=data.get("nombre"))
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"message": "Creado", "data": nuevo.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
```

---

### 📝 "¿Cómo llamo APIs desde JavaScript?"

```javascript
// GET
const token = localStorage.getItem('access_token');
const response = await fetch('/api/admin/datos', {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
console.log(data);

// POST
const response = await fetch('/api/admin/datos', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ nombre: "Nuevo" })
});
const result = await response.json();

// PATCH
const response = await fetch('/api/admin/datos/1', {
    method: 'PATCH',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ nombre: "Actualizado" })
});
```

---

## 3️⃣ Patrones de Código Comunes

### 🔄 Patrón CRUD Completo

**Modelo** (`app/models/example.py`):
```python
class Example(db.Model):
    __tablename__ = 'examples'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
```

**Controller** (`app/controllers/admin_controller.py`):
```python
# CREATE - GET (mostrar formulario)
@admin_bp.get("/example/create")
def example_create_view():
    return render_template("admin/example_create.html")

# CREATE - POST (guardar)
@admin_bp.post("/example/create")
def example_create_action():
    try:
        name = request.form.get("name")
        description = request.form.get("description")
        example = Example(name=name, description=description)
        db.session.add(example)
        db.session.commit()
        flash("Creado exitosamente", "success")
        return redirect(url_for("admin.example_view"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("admin.example_create_view"))

# READ - Lista
@admin_bp.get("/example")
def example_view():
    examples = Example.query.all()
    return render_template("admin/example.html", examples=examples)

# UPDATE - GET (mostrar formulario pre-llenado)
@admin_bp.get("/example/<int:example_id>/edit")
def example_edit_view(example_id):
    example = Example.query.get_or_404(example_id)
    return render_template("admin/example_edit.html", example=example)

# UPDATE - POST (guardar cambios)
@admin_bp.post("/example/<int:example_id>/edit")
def example_edit_action(example_id):
    try:
        example = Example.query.get_or_404(example_id)
        example.name = request.form.get("name")
        example.description = request.form.get("description")
        db.session.commit()
        flash("Actualizado exitosamente", "success")
        return redirect(url_for("admin.example_view"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("admin.example_edit_view", example_id=example_id))

# DELETE
@admin_bp.post("/example/<int:example_id>/delete")
def example_delete_action(example_id):
    try:
        example = Example.query.get_or_404(example_id)
        db.session.delete(example)
        db.session.commit()
        flash("Eliminado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("admin.example_view"))

# API - GET JSON
@admin_api_bp.get("/admin/examples")
@jwt_required()
def get_examples():
    examples = Example.query.all()
    return jsonify({"data": [e.to_dict() for e in examples]})
```

---

## 4️⃣ Estructura de Archivos Rápida

```
Para una nueva característica "Solicitudes":

app/
├── models/
│   └── solicitud.py                    # Modelo Solicitud
├── controllers/
│   └── admin_controller.py             # Rutas @admin_bp, @admin_api_bp
├── services/
│   └── solicitud_service.py            # Lógica (opcional)
└── views/
    └── admin/
        ├── solicitud.html              # Lista
        ├── solicitud_create.html       # Crear
        └── solicitud_edit.html         # Editar

migrations/
└── versions/
    └── XXXXXX_add_solicitud.py         # Auto-generado por flask db migrate
```

---

## 5️⃣ Checklist para Nueva Feature

- [ ] Modelo en `app/models/`
- [ ] Migración: `flask db migrate` + `flask db upgrade`
- [ ] Controller: vistas GET/POST en `admin_controller.py`
- [ ] Templates HTML en `app/views/admin/`
- [ ] Estilos Bootstrap 4 + SB Admin 2 aplicados
- [ ] APIs JSON en `@admin_api_bp`
- [ ] Protección con `@jwt_required()` donde sea necesario
- [ ] Flash messages para éxito/error
- [ ] Validación de inputs en servidor
- [ ] Tests (si existen en el proyecto)
- [ ] Documentación de cambios en PR

---

## 6️⃣ Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `ImportError: cannot import name 'X'` | Ruta incorrecta en import | Verificar ruta exacta: `from app.models import User` |
| `AttributeError: 'X' object has no attribute 'Y'` | Campo no existe en modelo | Verificar `app/models/X.py` y hacer migración |
| `404 Template not found: 'admin/X.html'` | Archivo HTML no existe | Crear en `app/views/admin/X.html` |
| `TypeError: render_template() missing required positional argument 'X'` | Variable no pasada a template | Agregar parámetro en `render_template(..., X=valor)` |
| `IntegrityError: Duplicate entry` | Constraint violado (unique, FK, etc.) | Validar datos antes de `db.session.add()` |
| `401 Unauthorized` en API | Token faltante o inválido | Incluir header `Authorization: Bearer <token>` |

---

## 7️⃣ Comandos Útiles

```bash
# Desarrollo
python run.py                          # Ejecutar servidor
python -m flask db migrate -m "msg"   # Crear migración
python -m flask db upgrade            # Aplicar migraciones
python -m flask db downgrade          # Revertir última migración
python update_db.py                   # Sembrar datos demo

# Debugging
python -m flask shell                 # Consola interactiva
>>> from app.models import *
>>> Student.query.count()

# Docker
docker compose up --build             # Levantar servicios
docker compose down                   # Apagar servicios
docker compose logs -f app            # Ver logs en tiempo real

# Git
git checkout -b feature/nombre        # Nueva rama
git add .                             # Stage cambios
git commit -m "feat: descripción"    # Commit
git push origin feature/nombre        # Push
```

---

## 8️⃣ Comunicación Efectiva entre IAs

### ✅ LO QUE FUNCIONA
> "Agrega un campo `estado` (enum: pendiente/aprobado/rechazado) al modelo Solicitud. Crea vistas HTML para listar, crear y editar solicitudes con validación en servidor. Asegúrate de usar Bootstrap 4 y SB Admin 2 para consistencia visual."

### ❌ LO QUE NO FUNCIONA
> "Hazme una página nueva"

### ✅ CONTEXTO ÚTIL
1. **Archivo/componente específico**: "En `app/models/solicitud.py`, agrega..."
2. **Error exacto**: "El template `admin/solicitud.html` da `404`, necesito..."
3. **Patrón a seguir**: "Crea esto siguiendo el patrón CRUD de `Example` en el código"
4. **Restricciones**: "Solo admin (rol=admin) puede ver solicitudes"

---

## 9️⃣ Referencias Rápidas por IA

### Copilot/ChatGPT
- Sistema de solicitudes: Usado para CRUD de entidades
- Validación: Server-side en controller
- Seguridad: JWT + `@jwt_required()`

### Claude
- Arquitectura MVC explícita
- Separación de responsabilidades clara
- Documentación inline en código

### Gemini
- Visualización de flujos (diagramas ER)
- Optimización de queries SQLAlchemy
- Mejoras de performance

---

## 🔟 Próximas Características Planeadas

- [ ] Sistema de notificaciones en tiempo real (WebSockets)
- [ ] Importar asistencia desde Excel
- [ ] Reporte de asistencia en PDF
- [ ] Integración con Google Classroom
- [ ] Panel de IA para detección de bajo rendimiento
- [ ] Tests automatizados (pytest)
- [ ] API GraphQL (alternativa a REST)

---

## 📞 Contacto y Preguntas

Si otra IA tiene preguntas:
1. Revisar este documento
2. Revisar `RESUMEN_PROYECTO.md`
3. Revisar `README.md`
4. Revisar código en `app/models/`, `app/controllers/`
5. Hacer pregunta específica con contexto

---

**Última actualización**: Diciembre 2025  
**Versión**: 1.0  
**Autor**: Equipo de Desarrollo CogniPass
