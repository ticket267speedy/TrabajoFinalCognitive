# Estructura de Modelos y Relaciones - Referencia Completa

## Diagrama de Relaciones

```
┌─────────────────┐
│      User       │
│   (admin/      │
│   profesor)     │
└────────┬────────┘
         │
         │ One-to-Many (FK: admin_id)
         ├─────────────────────────────────┐
         │                                 │
         v                                 v
    ┌─────────────┐            ┌──────────────────────┐
    │   Course    │            │ AdvisorCourseLink    │
    │  (Clase)    │            │  (Vínculo Asesor)    │
    └──────┬──────┘            └──────────────────────┘
           │
           │ One-to-Many
           ├────────────┬────────────┬──────────────────┐
           │            │            │                  │
           v            v            v                  v
      ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐
      │Enrollment│ │Attendance│ │  Alert   │ │AdvisorCourseLink
      │ (Matríc) │ │(Asisten) │ │(Notif)   │ │ (duplicado)
      └────┬─────┘ └──────────┘ └──────────┘ └────────────────┘
           │
           │ Many-to-One (FK: student_id)
           │
           v
      ┌──────────────┐
      │  Student     │
      │  (Alumno)    │
      └──────┬───────┘
             │
             │ One-to-Many
             ├─────────────┬──────────────┐
             │             │              │
             v             v              v
        ┌─────────┐  ┌──────────┐  ┌──────────┐
        │Enrollment│  │Attendance│  │  Alert   │
        │(Matríc)  │  │(Asisten) │  │(Notif)   │
        └───────────┘  └──────────┘  └──────────┘
```

## Modelos Detallados

### 1. **User** (Usuario/Administrador/Profesor)

**Tabla:** `users`

**Columnas:**
- `id` (PK)
- `email` (UNIQUE)
- `password_text`
- `first_name`
- `last_name`
- `profile_photo_url`
- `role` (ENUM: admin, client, advisor)
- `created_at`

**Relaciones:**

```python
# Un User puede dictar muchos Courses
user.courses_dictated  # List[Course]

# Un User (advisor) puede estar vinculado a muchos Courses
user.advisor_links  # List[AdvisorCourseLink]

# Un User (advisor) puede estar referido desde AdvisorCourseLink
user.advisor_user  # (backref desde AdvisorCourseLink)
```

**Uso:**
```python
# Obtener todos los cursos que dicta un profesor
admin = User.query.get(1)
cursos = admin.courses_dictated  # One-to-Many relationship

# Obtener todos los vínculos de asesoramiento de un usuario
liens = admin.advisor_links  # One-to-Many relationship
```

---

### 2. **Course** (Curso/Clase)

**Tabla:** `courses`

**Columnas:**
- `id` (PK)
- `name`
- `admin_id` (FK → users.id)
- `start_time`
- `end_time`
- `days_of_week`
- `created_at`

**Relaciones:**

```python
# Un Course pertenece a un User (profesor/admin)
course.instructor  # User (backref desde User.courses_dictated)

# Un Course tiene muchas Enrollments (matrículas)
course.enrollments  # List[Enrollment]

# Un Course tiene muchas Attendances (registros de asistencia)
course.attendances  # List[Attendance]

# Un Course tiene muchas Alerts (alertas)
course.alerts  # List[Alert]

# Un Course puede tener muchos AdvisorCourseLinks
course.advisor_links  # List[AdvisorCourseLink]
```

**Uso:**
```python
# Obtener el profesor de un curso
course = Course.query.get(1)
profesor = course.instructor  # User object

# Obtener todos los estudiantes matriculados
enrollments = course.enrollments  # List[Enrollment]
estudiantes = [e.student for e in enrollments]

# Obtener registros de asistencia
asistencias = course.attendances  # List[Attendance]

# Obtener todas las alertas del curso
alertas = course.alerts  # List[Alert]
```

---

### 3. **Student** (Estudiante)

**Tabla:** `students`

**Columnas:**
- `id` (PK)
- `first_name`
- `last_name`
- `email`
- `is_scholarship_student`
- `profile_photo_url`
- `created_at`

**Relaciones:**

```python
# Un Student tiene muchas Enrollments
student.enrollments  # List[Enrollment]

# Un Student tiene muchas Attendances
student.attendances  # List[Attendance]

# Un Student puede tener muchas Alerts
student.alerts  # List[Alert]
```

**Uso:**
```python
# Obtener todos los cursos en los que está matriculado
estudiante = Student.query.get(1)
matrículas = estudiante.enrollments  # List[Enrollment]
cursos = [e.course for e in matrículas]

# Obtener registros de asistencia del estudiante
asistencias = estudiante.attendances  # List[Attendance]

# Obtener alertas del estudiante
alertas = estudiante.alerts  # List[Alert]
```

---

### 4. **Enrollment** (Matrícula)

**Tabla:** `enrollments`

**Columnas:**
- `id` (PK)
- `student_id` (FK → students.id)
- `course_id` (FK → courses.id)
- `created_at`

**Relaciones:**

```python
# Un Enrollment pertenece a un Student
enrollment.student  # Student (backref desde Student.enrollments)

# Un Enrollment pertenece a un Course
enrollment.course  # Course (backref desde Course.enrollments)
```

**Uso:**
```python
# Obtener información del estudiante y curso matriculado
matricula = Enrollment.query.get(1)
estudiante = matricula.student  # Student object
curso = matricula.course  # Course object

# Listar todos los estudiantes de un curso
curso = Course.query.get(1)
estudiantes = [e.student for e in curso.enrollments]

# Listar todos los cursos de un estudiante
estudiante = Student.query.get(1)
cursos = [e.course for e in estudiante.enrollments]
```

---

### 5. **Attendance** (Asistencia)

**Tabla:** `attendance`

**Columnas:**
- `id` (PK)
- `student_id` (FK → students.id)
- `course_id` (FK → courses.id)
- `date`
- `entry_time`
- `exit_time`
- `status` (ENUM: presente, tardanza, falta, salida_repentina)
- `created_at`

**Relaciones:**

```python
# Un Attendance pertenece a un Student
attendance.student  # Student (backref desde Student.attendances)

# Un Attendance pertenece a un Course
attendance.course  # Course (backref desde Course.attendances)
```

**Uso:**
```python
# Obtener información de asistencia
asistencia = Attendance.query.get(1)
estudiante = asistencia.student  # Student object
curso = asistencia.course  # Course object

# Obtener asistencias de un estudiante en un curso
asistencias = Attendance.query.filter_by(
    student_id=1, 
    course_id=1
).all()

# Obtener asistencias de un día
from datetime import date
asistencias_hoy = Attendance.query.filter_by(date=date.today()).all()
```

---

### 6. **Alert** (Alerta/Notificación)

**Tabla:** `alerts`

**Columnas:**
- `id` (PK)
- `student_id` (FK → students.id)
- `course_id` (FK → courses.id, nullable)
- `message`
- `is_read`
- `created_at`

**Relaciones:**

```python
# Una Alert pertenece a un Student
alert.student  # Student (backref desde Student.alerts)

# Una Alert pertenece a un Course (opcional)
alert.course  # Course (backref desde Course.alerts)
```

**Uso:**
```python
# Obtener información de una alerta
alerta = Alert.query.get(1)
estudiante = alerta.student  # Student object
curso = alerta.course  # Course object (puede ser None)

# Obtener alertas no leídas de un estudiante
alertas = Alert.query.filter_by(student_id=1, is_read=False).all()

# Marcar alerta como leída
alerta.is_read = True
db.session.commit()
```

---

### 7. **AdvisorCourseLink** (Vínculo Asesor-Curso)

**Tabla:** `advisor_course_links`

**Columnas:**
- `id` (PK)
- `course_id` (FK → courses.id)
- `advisor_user_id` (FK → users.id)
- `status` (ENUM: invited, requested, accepted, rejected)
- `initiated_by` (ENUM: professor, advisor, system)
- `created_at`
- `updated_at`
- `accepted_at` (nullable)
- `rejected_reason` (nullable)

**Relaciones:**

```python
# Un AdvisorCourseLink pertenece a un Course
link.course  # Course (backref desde Course.advisor_links)

# Un AdvisorCourseLink pertenece a un User (advisor)
link.advisor_user  # User (backref desde User.advisor_links)
```

**Uso:**
```python
# Obtener información del vínculo
vinculo = AdvisorCourseLink.query.get(1)
curso = vinculo.course  # Course object
asesor = vinculo.advisor_user  # User object

# Obtener todos los asesores de un curso
curso = Course.query.get(1)
asesores = [l.advisor_user for l in curso.advisor_links if l.status == 'accepted']

# Obtener todos los cursos asesorados por un usuario
asesor = User.query.get(1)
cursos_asesorados = [l.course for l in asesor.advisor_links if l.status == 'accepted']
```

---

## Ejemplos Prácticos Completos

### Ejemplo 1: Obtener todos los estudiantes de un curso específico

```python
curso = Course.query.get(1)
estudiantes = [e.student for e in curso.enrollments]

# O más explícito:
matrículas = Enrollment.query.filter_by(course_id=1).all()
estudiantes = [m.student for m in matrículas]
```

### Ejemplo 2: Registrar asistencia de un estudiante

```python
from datetime import date, time

asistencia = Attendance(
    student_id=1,
    course_id=1,
    date=date.today(),
    entry_time=time(8, 15),
    exit_time=time(11, 45),
    status='presente'
)
db.session.add(asistencia)
db.session.commit()
```

### Ejemplo 3: Obtener datos completos de una matrícula

```python
matricula = Enrollment.query.get(1)
print(f"Estudiante: {matricula.student.first_name} {matricula.student.last_name}")
print(f"Curso: {matricula.course.name}")
print(f"Profesor: {matricula.course.instructor.first_name} {matricula.course.instructor.last_name}")
```

### Ejemplo 4: Listar asistencias de un estudiante en un curso

```python
asistencias = Attendance.query.filter_by(
    student_id=1,
    course_id=1
).order_by(Attendance.date.desc()).all()

for asist in asistencias:
    print(f"{asist.date}: {asist.status} ({asist.entry_time} - {asist.exit_time})")
```

### Ejemplo 5: Navegar cascada de relaciones

```python
# Empezando por un User
user = User.query.get(1)

# Obtener sus cursos
for curso in user.courses_dictated:
    print(f"Curso: {curso.name}")
    
    # Obtener estudiantes del curso
    for matricula in curso.enrollments:
        estudiante = matricula.student
        print(f"  - {estudiante.first_name} {estudiante.last_name}")
        
        # Obtener asistencias del estudiante
        for asistencia in estudiante.attendances:
            if asistencia.course_id == curso.id:
                print(f"    Asistencia {asistencia.date}: {asistencia.status}")
```

---

## Cascada de Eliminación (Cascade Delete)

Todas las relaciones tienen `cascade='all, delete-orphan'`. Esto significa:

```python
# Si eliminas un Course, se eliminarán automáticamente:
# - Todos sus Enrollments
# - Todos sus Attendances
# - Todos sus Alerts
# - Todos sus AdvisorCourseLinks

curso = Course.query.get(1)
db.session.delete(curso)
db.session.commit()  # Todo cascada se borra automáticamente

# Si eliminas un Student, se eliminarán automáticamente:
# - Todos sus Enrollments
# - Todos sus Attendances
# - Todas sus Alerts

estudiante = Student.query.get(1)
db.session.delete(estudiante)
db.session.commit()  # Todo cascada se borra automáticamente
```

---

## Acceso Bidireccional

Gracias a los `backref`, puedes acceder desde cualquier dirección:

```python
# Desde Course hacia Student
curso = Course.query.get(1)
for matricula in curso.enrollments:
    print(matricula.student.first_name)

# Desde Student hacia Course
estudiante = Student.query.get(1)
for matricula in estudiante.enrollments:
    print(matricula.course.name)

# Desde Attendance
asistencia = Attendance.query.get(1)
print(asistencia.student.first_name)  # Acceso bidireccional
print(asistencia.course.name)  # Acceso bidireccional
```

---

## Resumen de Backrefs Disponibles

| Modelo | Backref Name | Tipo | Desde |
|--------|--------------|------|-------|
| User | courses_dictated | One-to-Many | User → Course |
| User | advisor_links | One-to-Many | User → AdvisorCourseLink |
| Course | instructor | Many-to-One | Course → User |
| Course | enrollments | One-to-Many | Course → Enrollment |
| Course | attendances | One-to-Many | Course → Attendance |
| Course | alerts | One-to-Many | Course → Alert |
| Course | advisor_links | One-to-Many | Course → AdvisorCourseLink |
| Student | enrollments | One-to-Many | Student → Enrollment |
| Student | attendances | One-to-Many | Student → Attendance |
| Student | alerts | One-to-Many | Student → Alert |
| Enrollment | student | Many-to-One | Enrollment → Student |
| Enrollment | course | Many-to-One | Enrollment → Course |
| Attendance | student | Many-to-One | Attendance → Student |
| Attendance | course | Many-to-One | Attendance → Course |
| Alert | student | Many-to-One | Alert → Student |
| Alert | course | Many-to-One | Alert → Course |
| AdvisorCourseLink | course | Many-to-One | AdvisorCourseLink → Course |
| AdvisorCourseLink | advisor_user | Many-to-One | AdvisorCourseLink → User |

---

## Foreign Keys Definidas

Todas las Foreign Keys están correctamente definidas en las tablas hijas:

| Tabla | Columna | Referencia |
|-------|---------|-----------|
| courses | admin_id | users.id |
| enrollments | student_id | students.id |
| enrollments | course_id | courses.id |
| attendance | student_id | students.id |
| attendance | course_id | courses.id |
| alerts | student_id | students.id |
| alerts | course_id | courses.id |
| advisor_course_links | course_id | courses.id |
| advisor_course_links | advisor_user_id | users.id |

---

## Validación en PostgreSQL

Para verificar las relaciones en tu BD de Supabase:

```sql
-- Ver todas las Foreign Keys
SELECT constraint_name, table_name, column_name, foreign_table_name, foreign_column_name
FROM information_schema.key_column_usage
WHERE table_schema = 'public'
ORDER BY table_name;

-- Ver relaciones específicas
SELECT *
FROM pg_constraint
WHERE conname LIKE '%fk%'
ORDER BY conname;
```

---

## Conclusión

✅ Todos los modelos están correctamente estructurados con:
- Foreign Keys explícitas
- Relaciones bidireccionales con backrefs
- Cascade delete para integridad referencial
- Lazy loading configurado
- Nombres descriptivos para fácil acceso

Puedes usar cualquier combinación de acceso a través de las relaciones y todo funciona correctamente.
