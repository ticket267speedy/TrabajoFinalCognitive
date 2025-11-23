# Referencia Rápida de Relaciones - Cheat Sheet

## 📋 Acceso Rápido a Relaciones

### User Model
```python
user = User.query.get(1)

# ✅ Obtener todos los cursos que dicta
cursos = user.courses_dictated

# ✅ Obtener todos sus vínculos como asesor
vinculos = user.advisor_links
```

### Course Model
```python
curso = Course.query.get(1)

# ✅ Obtener el profesor/instructor
profesor = curso.instructor

# ✅ Obtener todos los estudiantes matriculados
matrículas = curso.enrollments
estudiantes = [m.student for m in matrículas]

# ✅ Obtener todos los registros de asistencia
asistencias = curso.attendances

# ✅ Obtener todas las alertas
alertas = curso.alerts

# ✅ Obtener todos los asesores
asesores = [l.advisor_user for l in curso.advisor_links if l.status == 'accepted']
```

### Student Model
```python
estudiante = Student.query.get(1)

# ✅ Obtener todos los cursos en los que está matriculado
matrículas = estudiante.enrollments
cursos = [m.course for m in matrículas]

# ✅ Obtener todos sus registros de asistencia
asistencias = estudiante.attendances

# ✅ Obtener todas sus alertas
alertas = estudiante.alerts
```

### Enrollment Model
```python
matricula = Enrollment.query.get(1)

# ✅ Obtener el estudiante de esta matrícula
estudiante = matricula.student

# ✅ Obtener el curso de esta matrícula
curso = matricula.course
```

### Attendance Model
```python
asistencia = Attendance.query.get(1)

# ✅ Obtener el estudiante
estudiante = asistencia.student

# ✅ Obtener el curso
curso = asistencia.course

# ✅ Acceder a sus datos
print(f"{asistencia.date}: {asistencia.status}")
print(f"Entrada: {asistencia.entry_time}, Salida: {asistencia.exit_time}")
```

### Alert Model
```python
alerta = Alert.query.get(1)

# ✅ Obtener el estudiante
estudiante = alerta.student

# ✅ Obtener el curso (puede ser None)
curso = alerta.course
```

### AdvisorCourseLink Model
```python
vinculo = AdvisorCourseLink.query.get(1)

# ✅ Obtener el curso
curso = vinculo.course

# ✅ Obtener el asesor
asesor = vinculo.advisor_user

# ✅ Verificar estado
print(vinculo.status)  # invited, requested, accepted, rejected
```

---

## 🔄 Cascadas Comunes

### Eliminar un Course (borra todo relacionado)
```python
curso = Course.query.get(1)
db.session.delete(curso)
db.session.commit()

# Automáticamente se eliminan:
# - Todas sus Enrollments
# - Todas sus Attendances
# - Todas sus Alerts
# - Todos sus AdvisorCourseLinks
```

### Eliminar un Student (borra todo relacionado)
```python
estudiante = Student.query.get(1)
db.session.delete(estudiante)
db.session.commit()

# Automáticamente se eliminan:
# - Todas sus Enrollments
# - Todas sus Attendances
# - Todas sus Alerts
```

### Eliminar un User (borra todo relacionado)
```python
user = User.query.get(1)
db.session.delete(user)
db.session.commit()

# Automáticamente se eliminan:
# - Todos sus Courses
# - Y todo lo relacionado a esos cursos...
```

---

## 🔍 Queries Comunes

### Obtener todos los estudiantes de un curso
```python
curso_id = 1
estudiantes = db.session.query(Student).join(
    Enrollment, Enrollment.student_id == Student.id
).filter(Enrollment.course_id == curso_id).all()

# O más simple con relaciones:
curso = Course.query.get(1)
estudiantes = [m.student for m in curso.enrollments]
```

### Obtener todos los cursos de un estudiante
```python
estudiante_id = 1
cursos = db.session.query(Course).join(
    Enrollment, Enrollment.course_id == Course.id
).filter(Enrollment.student_id == estudiante_id).all()

# O más simple con relaciones:
estudiante = Student.query.get(1)
cursos = [m.course for m in estudiante.enrollments]
```

### Obtener asistencia de un estudiante en un curso
```python
estudiante_id = 1
curso_id = 1
asistencias = Attendance.query.filter_by(
    student_id=estudiante_id,
    course_id=curso_id
).all()
```

### Obtener asistencias de hoy
```python
from datetime import date
asistencias_hoy = Attendance.query.filter_by(date=date.today()).all()
```

### Obtener cursos enseñados por un profesor
```python
profesor_id = 1
cursos = User.query.get(profesor_id).courses_dictated
```

### Obtener asesores de un curso
```python
curso_id = 1
asesores = db.session.query(User).join(
    AdvisorCourseLink, AdvisorCourseLink.advisor_user_id == User.id
).filter(
    AdvisorCourseLink.course_id == curso_id,
    AdvisorCourseLink.status == 'accepted'
).all()

# O más simple:
curso = Course.query.get(1)
asesores = [l.advisor_user for l in curso.advisor_links if l.status == 'accepted']
```

---

## 📊 Estadísticas

### Contar estudiantes de un curso
```python
curso_id = 1
count = Enrollment.query.filter_by(course_id=curso_id).count()
```

### Contar asistencias presentes
```python
from datetime import date
presentes_hoy = Attendance.query.filter_by(
    date=date.today(),
    status='presente'
).count()
```

### Obtener estudiantes con alertas no leídas
```python
estudiantes_con_alertas = db.session.query(Student).join(
    Alert, Alert.student_id == Student.id
).filter(Alert.is_read == False).distinct().all()
```

---

## 🛠️ Crear Nuevos Registros

### Crear una matrícula
```python
nueva_matricula = Enrollment(
    student_id=1,
    course_id=1
)
db.session.add(nueva_matricula)
db.session.commit()
```

### Crear un registro de asistencia
```python
from datetime import date, time

nueva_asistencia = Attendance(
    student_id=1,
    course_id=1,
    date=date.today(),
    entry_time=time(8, 15),
    exit_time=time(11, 45),
    status='presente'
)
db.session.add(nueva_asistencia)
db.session.commit()
```

### Crear una alerta
```python
nueva_alerta = Alert(
    student_id=1,
    course_id=1,
    message="El estudiante no asistió a clase",
    is_read=False
)
db.session.add(nueva_alerta)
db.session.commit()
```

### Crear un vínculo de asesor
```python
nuevo_vinculo = AdvisorCourseLink(
    course_id=1,
    advisor_user_id=2,
    status='invited',
    initiated_by='professor'
)
db.session.add(nuevo_vinculo)
db.session.commit()
```

---

## ✏️ Actualizar Registros

### Cambiar estado de asistencia
```python
asistencia = Attendance.query.get(1)
asistencia.status = 'tardanza'
db.session.commit()
```

### Marcar alerta como leída
```python
alerta = Alert.query.get(1)
alerta.is_read = True
db.session.commit()
```

### Aceptar vínculo de asesor
```python
vinculo = AdvisorCourseLink.query.get(1)
vinculo.status = 'accepted'
db.session.commit()
```

---

## 🔗 Navegación Completa

### Desde un User hacia Asistencias
```python
user = User.query.get(1)
for curso in user.courses_dictated:
    print(f"Curso: {curso.name}")
    for asistencia in curso.attendances:
        print(f"  - {asistencia.student.first_name}: {asistencia.status}")
```

### Desde una Asistencia hacia el Profesor
```python
asistencia = Attendance.query.get(1)
curso = asistencia.course
profesor = curso.instructor
print(f"Profesor: {profesor.first_name} {profesor.last_name}")
```

### Cascada Completa
```python
# Obtener un estudiante
estudiante = Student.query.get(1)

# Obtener sus matrículas
for matricula in estudiante.enrollments:
    curso = matricula.course
    
    # Obtener el profesor del curso
    profesor = curso.instructor
    print(f"{estudiante.first_name} está en {curso.name} con {profesor.first_name}")
    
    # Obtener su asistencia en este curso
    for asistencia in estudiante.attendances:
        if asistencia.course_id == curso.id:
            print(f"  {asistencia.date}: {asistencia.status}")
```

---

## 📝 Notas Importantes

### ⚠️ Lazy Loading
Las relaciones se cargan bajo demanda:
```python
user = User.query.get(1)  # NO carga cursos aquí
cursos = user.courses_dictated  # Aquí se cargan
```

### ⚠️ N+1 Problem
Ten cuidado con loops que provocan múltiples queries:
```python
# ❌ MAL: Esto hace N+1 queries
for curso in courses:
    print(curso.instructor.first_name)  # Cada instructor es una query

# ✅ BIEN: Usa joinedload
from sqlalchemy.orm import joinedload
cursos = Course.query.options(joinedload(Course.instructor)).all()
for curso in cursos:
    print(curso.instructor.first_name)  # Sin queries adicionales
```

### ⚠️ Cascade Delete
Eliminar un objeto elimina automáticamente los relacionados:
```python
db.session.delete(curso)  # Borra el curso Y sus matrículas
```

---

## 🆚 Antes vs Después

### Antes (Sin relaciones bidireccionales)
```python
# ❌ Acceso limitado
curso = Course.query.get(1)
print(curso.admin)  # Devolvía None o error

# Tenías que usar queries manuales
from sqlalchemy import and_
matrículas = Enrollment.query.filter(
    and_(
        Enrollment.student_id == 1,
        Enrollment.course_id == 1
    )
).all()
```

### Después (Con relaciones bidireccionales)
```python
# ✅ Acceso simple e intuitivo
curso = Course.query.get(1)
print(curso.instructor)  # Devuelve el User object

# Acceso directo vía relaciones
curso = Course.query.get(1)
matrículas = curso.enrollments
estudiantes = [m.student for m in matrículas]
```

---

## ✅ Checklist de Uso

- [ ] Usando `user.courses_dictated` en lugar de queries manuales
- [ ] Usando `course.instructor` en lugar de `course.admin`
- [ ] Usando `course.enrollments` para obtener matrículas
- [ ] Usando `student.attendances` para asistencias
- [ ] Usando backrefs como `enrollment.student` y `enrollment.course`
- [ ] Recordando que cascade delete borra datos relacionados
- [ ] Evitando N+1 problems con joinedload cuando sea necesario
- [ ] Verificando que los datos se cargan correctamente

---

**Última actualización**: 22 de Noviembre, 2025
**Status**: ✅ Listo para usar
