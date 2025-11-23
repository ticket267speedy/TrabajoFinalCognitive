# API Endpoints - Referencia Rápida

## 🔐 Autenticación
Todos los endpoints requieren:
```
Header: Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## 📚 Gestión de Cursos

### 1. Listar Cursos
```
GET /api/admin/courses
Authorization: Bearer <token>

Response (200):
[
  {
    "id": 1,
    "name": "Matemáticas",
    "admin_id": 5,
    "enrollments": [...],
    "class_sessions": [...]
  },
  ...
]
```

### 2. Crear Curso
```
POST /api/admin/courses
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "name": "Física Avanzada",
  "admin_id": 5
}

Response (201):
{
  "id": 3
}
```

### 3. Editar Curso
```
PUT /api/admin/courses/1
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "name": "Matemáticas Básicas",
  "admin_id": 5
}

Response (200):
{
  "status": "updated"
}
```

### 4. Eliminar Curso
```
DELETE /api/admin/courses/1
Authorization: Bearer <token>

Response (200):
{
  "status": "deleted"
}
```

---

## 👥 Gestión de Estudiantes en Curso

### 5. Listar Estudiantes de un Curso
```
GET /api/admin/courses/1/students
Authorization: Bearer <token>

Response (200):
[
  {
    "id": 10,
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "is_scholarship_student": true
  },
  ...
]
```

### 6. Agregar Estudiante a Curso
```
POST /api/admin/courses/1/enroll
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "student_id": 10
}

Response (201):
{
  "id": 1,
  "course_id": 1,
  "student_id": 10
}

Errores:
- 400: Si student_id falta o estudiante ya está inscrito
- 404: Si estudiante no existe
```

### 7. Eliminar Estudiante de Curso
```
DELETE /api/admin/courses/1/unenroll/10
Authorization: Bearer <token>

Response (200):
{
  "status": "deleted"
}

Errores:
- 404: Si enrollment no existe
```

---

## 📖 Gestión General de Estudiantes

### 8. Listar Todos los Estudiantes
```
GET /api/admin/students
Authorization: Bearer <token>

Query Parameters (opcionales):
?scholarship=true  → Solo becarios
?scholarship=false → Solo no becarios

Response (200):
[
  {
    "id": 10,
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "is_scholarship_student": true,
    "courses": ["Matemáticas", "Física"]
  },
  ...
]
```

### 9. Crear Estudiante
```
POST /api/admin/students
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "first_name": "Carlos",
  "last_name": "López",
  "email": "carlos@example.com",
  "is_scholarship_student": false
}

Response (201):
{
  "id": 11
}

Errores:
- 400: Si faltan first_name o last_name
```

### 10. Editar Estudiante
```
PATCH /api/admin/students/10
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "first_name": "Juan",
  "last_name": "Pérez García",
  "email": "juan.perez@example.com",
  "is_scholarship_student": true
}

Response (200):
{
  "status": "updated"
}
```

### 11. Eliminar Estudiante
```
DELETE /api/admin/students/10
Authorization: Bearer <token>

Response (200):
{
  "status": "deleted"
}
```

---

## 🧑‍🏫 Gestión de Profesores (Users)

### 12. Listar Usuarios (Profesores)
```
GET /api/admin/users?role=admin
Authorization: Bearer <token>

Query Parameters (opcionales):
?role=admin   → Solo admin/profesores
?role=client  → Solo clientes

Response (200):
[
  {
    "id": 5,
    "email": "prof1@example.com",
    "first_name": "María",
    "last_name": "García",
    "role": "admin"
  },
  ...
]
```

---

## 🔍 Códigos de Respuesta

| Código | Significado |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Sin autenticación |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no existe |
| 500 | Server Error - Error del servidor |

---

## 💡 Ejemplos de Uso (JavaScript Fetch)

### Crear Curso
```javascript
const token = localStorage.getItem('access_token');
const response = await fetch('/api/admin/courses', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Nueva Clase',
    admin_id: 5
  })
});
const data = await response.json();
```

### Agregar Estudiante a Curso
```javascript
const response = await fetch('/api/admin/courses/1/enroll', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    student_id: 10
  })
});
```

### Listar Estudiantes de Curso
```javascript
const response = await fetch('/api/admin/courses/1/students', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const students = await response.json();
```

---

## ⚠️ Restricciones Importantes

1. **Admin-only**: Solo usuarios con role='admin' pueden acceder
2. **Own courses**: Un admin solo puede ver/editar sus propios cursos
3. **No duplicates**: No se puede inscribir un estudiante dos veces en el mismo curso
4. **Student exists**: El estudiante debe existir antes de inscribirse
5. **JWT required**: Todo endpoint requiere token válido

---

## 🔗 Rutas del Frontend

| Acción | Ruta | Verbo |
|--------|------|-------|
| Ver cursos | `/admin/courses` | GET |
| Crear curso | `/admin/courses/create` | GET |
| Editar curso | `/admin/courses/<id>/edit` | GET |
| Eliminar curso | `/admin/courses/<id>/delete` | GET |
| Ver estudiantes | `/admin/courses/<id>/students` | GET |

---

## 📞 Notas

- El token se obtiene después de login en `/login` o `/api/login`
- El token expira según configuración JWT (típicamente 24 horas)
- Todos los endpoints prefixados con `/api/admin/` son protegidos
- Base de datos: PostgreSQL (Supabase)
- Prefijo API detectado automáticamente: `/api/admin/` o `/admin/api/`

