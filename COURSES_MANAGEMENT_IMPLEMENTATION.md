# Gestión Completa de Cursos y Estudiantes - Implementación

## 📋 Resumen de Cambios

Se ha implementado un sistema completo de CRUD para cursos y estudiantes con páginas HTML separadas para cada operación, incluyendo paginación de estudiantes.

---

## 🏗️ Estructura de Archivos Creados/Modificados

### 1. **Vistas HTML (Nuevas)**

#### A. Gestión de Cursos
- **`app/views/admin/courses_list.html`** - Lista de todos los cursos con:
  - Tabla con: ID, Nombre, Profesor, Cantidad Estudiantes, Sesiones
  - Botones de Editar y Eliminar
  - Link para ver estudiantes del curso
  - Paginación (10 cursos por página)
  - Botón "Crear Curso"

- **`app/views/admin/courses_create.html`** - Formulario para crear nuevo curso:
  - Campo: Nombre del Curso
  - Campo: Profesor Asignado (select dropdown)
  - Botones: Crear Curso / Cancelar

- **`app/views/admin/courses_edit.html`** - Formulario para editar curso:
  - Pre-cargado con datos actuales del curso
  - Campos: Nombre, Profesor
  - Botones: Guardar Cambios / Cancelar
  - Detecta course_id desde URL

- **`app/views/admin/courses_delete.html`** - Página de confirmación de eliminación:
  - Muestra datos del curso a eliminar
  - Alert de advertencia
  - Checkbox de confirmación
  - Botón delete solo activo si checkbox está marcado

#### B. Gestión de Estudiantes por Curso
- **`app/views/admin/course_students.html`** - Página principal de estudiantes:
  - Nombre del curso en encabezado
  - Tabla de estudiantes con: ID, Nombre, Email, Becario, Asistencia
  - **Paginación: 5 estudiantes por página**
  - Botones Anterior/Siguiente para navegar
  - Indicador: "Página X de Y"
  - Modal para agregar estudiante (selector o crear nuevo)
  - Botones de Editar/Eliminar para cada estudiante
  - Botón "Volver a Cursos"

### 2. **Controlador de Vistas (Modificado)**

**`app/controllers/admin_controller.py`** - Se agregaron rutas:

```python
@admin_bp.get("/courses")  # Lista de cursos
@admin_bp.get("/courses/create")  # Crear curso
@admin_bp.get("/courses/<int:course_id>/edit")  # Editar curso
@admin_bp.get("/courses/<int:course_id>/delete")  # Eliminar curso
@admin_bp.get("/courses/<int:course_id>/students")  # Estudiantes del curso
```

### 3. **API Endpoints (Modificados)**

**`app/controllers/api.py`** - Se agregaron endpoints:

```python
# Estudiantes por Curso
GET    /admin/courses/<int:course_id>/students       # Listar estudiantes
POST   /admin/courses/<int:course_id>/enroll        # Agregar estudiante
DELETE /admin/courses/<int:course_id>/unenroll/<int:student_id>  # Eliminar
```

**Endpoints existentes utilizados:**
```python
POST   /admin/courses                     # Crear curso
GET    /admin/courses                     # Listar cursos
PUT    /admin/courses/<int:course_id>     # Editar curso
DELETE /admin/courses/<int:course_id>     # Eliminar curso
GET    /admin/students                    # Listar estudiantes
POST   /admin/students                    # Crear estudiante
PATCH  /admin/students/<int:student_id>   # Editar estudiante
DELETE /admin/students/<int:student_id>   # Eliminar estudiante
```

### 4. **Navegación (Modificado)**

**`app/views/layout.html`** - Actualizado:
- Link "Cursos" en sidebar ahora apunta a `/admin/courses` (antes era hash #courses)
- Mantiene estructura de menu existente

---

## 🔄 Flujo de Navegación

```
Dashboard
  ↓
[Menú Sidebar] → "Cursos"
  ↓
/admin/courses (Lista de Cursos)
  ├→ [Crear Curso] → /admin/courses/create
  ├→ [Editar] → /admin/courses/<id>/edit
  ├→ [Eliminar] → /admin/courses/<id>/delete
  └→ [Nombre Curso] → /admin/courses/<id>/students (Estudiantes)
      ├→ [Agregar Estudiante] → Modal (Crear/Seleccionar)
      ├→ [Editar Estudiante] → TODO (Implementar)
      ├→ [Eliminar Estudiante] → Confirmación en tabla
      ├→ [Anterior/Siguiente] → Paginación (5 por página)
      └→ [Volver a Cursos] → /admin/courses
```

---

## 📊 Características Principales

### Gestión de Cursos
✅ **Listar**: Tabla con paginación (10 por página)
✅ **Crear**: Formulario dedicado con validación
✅ **Editar**: Página separada con pre-carga de datos
✅ **Eliminar**: Página de confirmación con checkbox
✅ **Base de Datos**: Todos los cambios se persisten en BD

### Gestión de Estudiantes por Curso
✅ **Listar**: Tabla con **paginación de 5 por página**
✅ **Crear**: Modal para agregar existente o crear nuevo
✅ **Editar**: Botón disponible (lógica en API lista)
✅ **Eliminar**: Botón con confirmación de diálogo
✅ **Base de Datos**: Enrollments se persisten en BD
✅ **Validación**: No permite duplicados en inscripción

---

## 🔐 Autenticación y Autorización

- ✅ Todos los endpoints requieren JWT token (`@jwt_required()`)
- ✅ Solo admins pueden acceder (`_require_role("admin")`)
- ✅ Los cursos se filtran por admin_id (cada profesor ve solo sus cursos)
- ✅ Los estudiantes se validan antes de agregar a curso

---

## 📋 Métodos HTTP Utilizados

| Operación | Método | Endpoint | Status |
|-----------|--------|----------|--------|
| Listar cursos | GET | `/api/admin/courses` | ✅ Existente |
| Crear curso | POST | `/api/admin/courses` | ✅ Existente |
| Editar curso | PUT | `/api/admin/courses/<id>` | ✅ Existente |
| Eliminar curso | DELETE | `/api/admin/courses/<id>` | ✅ Existente |
| Listar estudiantes del curso | GET | `/api/admin/courses/<id>/students` | ✅ Nuevo |
| Agregar estudiante a curso | POST | `/api/admin/courses/<id>/enroll` | ✅ Nuevo |
| Eliminar estudiante de curso | DELETE | `/api/admin/courses/<id>/unenroll/<sid>` | ✅ Nuevo |

---

## 💾 Persistencia en Base de Datos

### Tablas Utilizadas
1. **courses** - Cursos (name, admin_id)
2. **enrollments** - Inscripciones (student_id, course_id)
3. **students** - Estudiantes (first_name, last_name, email, is_scholarship)
4. **users** - Profesores/Admins (para select dropdown)

### Relaciones
- `Course.admin_id` → `User.id` (Profesor del curso)
- `Enrollment.course_id` → `Course.id`
- `Enrollment.student_id` → `Student.id`

---

## 🎨 UI/UX

### Estilos Bootstrap 4
- Cards con shadow effects
- Badges para contar estudiantes/sesiones
- Botones de colores (Primary, Warning, Danger)
- Tablas responsive con scroll horizontal
- Modales para acciones secundarias

### Paginación
- **Cursos**: 10 por página (botones 1, 2, 3...)
- **Estudiantes**: 5 por página (botones Anterior/Siguiente)
- Indicador de página actual

### Mensajes Feedback
- Alertas de éxito (verde) - auto-desaparecen en 5s
- Alertas de error (rojo) - permanecen hasta cerrar
- Confirmaciones de diálogo (confirm()) antes de eliminar

---

## 🔧 Configuración API

### Headers Requeridos
```javascript
Authorization: Bearer <token>
Content-Type: application/json
```

### Detección de Prefijo API
El sistema detecta automáticamente si el prefijo API es:
- `/api/admin/` o
- `/admin/api/`

---

## 📱 Responsive Design

✅ Desktop (1920px) - Layout completo
✅ Tablet (768px) - Tabla scroll horizontal
✅ Mobile (375px) - Stack vertical, botones full-width

---

## 🧪 Próximos Pasos / TODO

- [ ] Implementar página de edición de estudiantes individual
- [ ] Agregar filtros avanzados en tabla de cursos
- [ ] Agregar horarios de clase (schedule) a cursos
- [ ] Implementar búsqueda en tiempo real
- [ ] Agregar exportar a PDF/Excel
- [ ] Implementar asignación de asesores a estudiantes
- [ ] Agregar logs de auditoría

---

## 📝 Notas Técnicas

### Validaciones Frontend
- Nombre de curso requerido
- Profesor requerido (select)
- Confirmación de eliminación
- Checkbox de confirmación en delete

### Validaciones Backend (API)
- JWT token requerido
- Rol admin requerido
- Curso debe pertenecer al admin
- Estudiante no puede inscribirse dos veces
- Estudiante debe existir antes de inscribir

### Error Handling
- Try-catch en todas las operaciones async
- Mensajes de error amigables
- Fallback a /admin/courses en errores críticos

---

## 🚀 Deployment

Para desplegar:
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar migraciones: `flask db upgrade`
3. Iniciar servidor: `python run.py`
4. Acceder a: `http://127.0.0.1:7000/admin/courses`

---

## 📞 Soporte

- Sistema guardado en: `TrabajoFinalCognitive/`
- Vistas: `app/views/admin/`
- Controladores: `app/controllers/`
- Base de datos: PostgreSQL (Supabase)

