# API Response Examples - Complete Reference

## 1. GET /api/admin/students

**Response with new "courses" field:**

```json
{
  "data": [
    {
      "id": 1,
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan@example.com",
      "is_scholarship_student": false,
      "profile_photo_url": "/uploads/photos/juan.jpg",
      "courses": ["Matemáticas", "Física", "Química"]
    },
    {
      "id": 2,
      "first_name": "María",
      "last_name": "García",
      "email": "maria@example.com",
      "is_scholarship_student": true,
      "profile_photo_url": "/uploads/photos/maria.jpg",
      "courses": ["Matemáticas", "Historia"]
    },
    {
      "id": 3,
      "first_name": "Carlos",
      "last_name": "López",
      "email": "carlos@example.com",
      "is_scholarship_student": false,
      "profile_photo_url": null,
      "courses": []
    }
  ]
}
```

**Frontend Implementation (students.html):**
```html
<!-- Rendered as -->
<tr>
  <td>1</td>
  <td>Juan Pérez</td>
  <td>juan@example.com</td>
  <td><span class="badge badge-secondary">Regular</span></td>
  <td>
    <span class="badge badge-info">Matemáticas</span>
    <span class="badge badge-info">Física</span>
    <span class="badge badge-info">Química</span>
  </td>
  <td>
    <button class="btn btn-sm btn-outline-primary">Editar</button>
    <button class="btn btn-sm btn-outline-danger">Eliminar</button>
  </td>
</tr>
```

---

## 2. GET /api/admin/courses/{course_id}/students

**URL Example:** `GET /api/admin/courses/1/students`

**Response:**

```json
{
  "data": [
    {
      "id": 1,
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan@example.com",
      "is_scholarship_student": false
    },
    {
      "id": 2,
      "first_name": "María",
      "last_name": "García",
      "email": "maria@example.com",
      "is_scholarship_student": true
    },
    {
      "id": 5,
      "first_name": "David",
      "last_name": "Rodríguez",
      "email": "david@example.com",
      "is_scholarship_student": false
    }
  ]
}
```

**Frontend Implementation (course_students.html):**
```html
<!-- Paginated table with 5 students per page -->
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Nombre</th>
      <th>Email</th>
      <th>Becario</th>
      <th>Asistencia</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Juan Pérez</td>
      <td>juan@example.com</td>
      <td><span class="badge badge-secondary">No</span></td>
      <td>--</td>
      <td>
        <button class="btn btn-sm">Editar</button>
        <button class="btn btn-sm">Eliminar</button>
      </td>
    </tr>
    <!-- More rows -->
  </tbody>
</table>
```

---

## 3. GET /api/admin/attendance

**Response:**

```json
{
  "data": [
    {
      "id": 1,
      "student_id": 1,
      "student_name": "Juan Pérez",
      "course_name": "Matemáticas",
      "date": "2024-01-15",
      "entry_time": "08:15:00",
      "exit_time": "11:45:00",
      "status": "presente"
    },
    {
      "id": 2,
      "student_id": 2,
      "student_name": "María García",
      "course_name": "Matemáticas",
      "date": "2024-01-15",
      "entry_time": "08:30:00",
      "exit_time": null,
      "status": "tardanza"
    },
    {
      "id": 3,
      "student_id": 3,
      "student_name": "Carlos López",
      "course_name": "Física",
      "date": "2024-01-15",
      "entry_time": null,
      "exit_time": null,
      "status": "falta"
    },
    {
      "id": 4,
      "student_id": 1,
      "student_name": "Juan Pérez",
      "course_name": "Física",
      "date": "2024-01-15",
      "entry_time": "09:00:00",
      "exit_time": "11:30:00",
      "status": "salida_repentina"
    }
  ]
}
```

**Frontend Implementation (attendance.html):**
```html
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Estudiante</th>
      <th>Curso</th>
      <th>Fecha</th>
      <th>Entrada</th>
      <th>Salida</th>
      <th>Estado</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Juan Pérez</td>
      <td>Matemáticas</td>
      <td>2024-01-15</td>
      <td>08:15</td>
      <td>11:45</td>
      <td><span class="badge badge-success">presente</span></td>
      <td><button class="btn btn-sm btn-outline-primary">Editar</button></td>
    </tr>
    <tr>
      <td>2</td>
      <td>María García</td>
      <td>Matemáticas</td>
      <td>2024-01-15</td>
      <td>08:30</td>
      <td>-</td>
      <td><span class="badge badge-warning">tardanza</span></td>
      <td><button class="btn btn-sm btn-outline-primary">Editar</button></td>
    </tr>
    <tr>
      <td>3</td>
      <td>Carlos López</td>
      <td>Física</td>
      <td>2024-01-15</td>
      <td>-</td>
      <td>-</td>
      <td><span class="badge badge-danger">falta</span></td>
      <td><button class="btn btn-sm btn-outline-primary">Editar</button></td>
    </tr>
  </tbody>
</table>
```

---

## 4. GET /api/admin/courses/{course_id}/attendance

**URL Example:** `GET /api/admin/courses/1/attendance`

**Response:**

```json
{
  "data": [
    {
      "id": 1,
      "student_id": 1,
      "student_name": "Juan Pérez",
      "entry_time": "08:15:00",
      "exit_time": "11:45:00",
      "status": "presente",
      "date": "2024-01-15"
    },
    {
      "id": 2,
      "student_id": 2,
      "student_name": "María García",
      "entry_time": "08:30:00",
      "exit_time": null,
      "status": "tardanza",
      "date": "2024-01-15"
    },
    {
      "id": 3,
      "student_id": 3,
      "student_name": "Carlos López",
      "entry_time": null,
      "exit_time": null,
      "status": "falta",
      "date": "2024-01-15"
    }
  ]
}
```

**Frontend Implementation (class-session.html):**
```html
<!-- In class-session.html, when user selects a course -->
<table>
  <thead>
    <tr>
      <th>Estudiante</th>
      <th>Entrada</th>
      <th>Salida</th>
      <th>Estado</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Juan Pérez</td>
      <td>08:15</td>
      <td>11:45</td>
      <td><span class="badge badge-success">presente</span></td>
      <td><button class="btn btn-sm btn-outline-primary edit-attendance-btn" data-id="1">Editar</button></td>
    </tr>
    <!-- More rows -->
  </tbody>
</table>
```

---

## 5. PATCH /api/admin/attendance/{attendance_id}

**URL Example:** `PATCH /api/admin/attendance/1`

**Request Body - Example 1 (Update Status):**
```json
{
  "status": "tardanza",
  "entry_time": null,
  "exit_time": null
}
```

**Request Body - Example 2 (Update Times):**
```json
{
  "status": "presente",
  "entry_time": "08:20",
  "exit_time": "11:50"
}
```

**Request Body - Example 3 (Full Update):**
```json
{
  "status": "presente",
  "entry_time": "08:15:30",
  "exit_time": "11:45:00"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Asistencia actualizada"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Status debe ser uno de: presente,tardanza,falta,salida_repentina"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Registro de asistencia no encontrado"
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": "No autorizado"
}
```

**Frontend Implementation (Modal Edit):**
```javascript
// When user clicks Edit button:
// 1. Modal opens with current values
document.getElementById('editAttendanceStatus').value = 'presente';
document.getElementById('editAttendanceEntry').value = '08:15';
document.getElementById('editAttendanceExit').value = '11:45';

// 2. User changes values in modal

// 3. User clicks "Guardar"
const payload = {
  status: 'tardanza',
  entry_time: '08:30',
  exit_time: '11:45'
};

const res = await fetch('/api/admin/attendance/1', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
});

// 4. Response handled and table refreshed
```

---

## Data Flow Summary

### Reading Student's Courses
```
User clicks /admin/students
  ↓
Frontend fetches GET /api/admin/students
  ↓
Backend queries students + enrollments
  ↓
Returns array with "courses" field
  ↓
Frontend renders table with course badges
```

### Reading Attendance for a Course
```
User selects course in /admin/class-session
  ↓
Frontend fetches GET /api/admin/courses/{id}/attendance
  ↓
Backend queries attendance where course_id = {id}
  ↓
Returns array with attendance records
  ↓
Frontend renders attendance table
```

### Updating Attendance
```
User clicks Edit on attendance record
  ↓
Modal opens with current values
  ↓
User modifies status/times
  ↓
User clicks Guardar
  ↓
Frontend sends PATCH /api/admin/attendance/{id}
  ↓
Backend updates Attendance record
  ↓
Responds with success/error
  ↓
Frontend closes modal and refreshes table
```

---

## Status Values Reference

| Status | Value | Display Color | Meaning |
|--------|-------|---------------|---------|
| Presente | `presente` | Green (success) | Student was on time |
| Tardanza | `tardanza` | Yellow (warning) | Student was late |
| Falta | `falta` | Red (danger) | Student was absent |
| Salida Repentina | `salida_repentina` | Blue (info) | Student left early |

---

## Time Format

- **Input Format**: `HH:MM` (e.g., "08:15", "11:45")
- **Output Format**: `HH:MM:SS` (e.g., "08:15:00")
- **Null/Empty**: Leave blank or send `null` if not applicable

---

## Error Scenarios

| Scenario | Status Code | Message |
|----------|-------------|---------|
| No JWT token | 401 | Unauthorized |
| Invalid JWT token | 401 | Unauthorized |
| User not admin role | 403 | No autorizado |
| Course not found | 404 | Curso no encontrado |
| Course not owned by admin | 404 | Curso no encontrado |
| Attendance not found | 404 | Registro de asistencia no encontrado |
| Invalid status value | 400 | Status debe ser uno de: ... |
| Database error | 500 | Server error details |

---

This reference covers all API responses and how they're used in the frontend!
