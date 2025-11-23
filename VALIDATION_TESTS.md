# Validación de Modelos - Test Script

Este documento contiene pruebas que puedes ejecutar para validar que todas las relaciones funcionan correctamente.

## 1. Validación de Imports

```python
# Verifica que todos los modelos se importan sin errores
from app.models import (
    User, Course, Student, Enrollment, Attendance, Alert, AdvisorCourseLink
)

print("✅ Todos los modelos se importaron correctamente")
```

## 2. Validación de Relaciones en User

```python
# Test: User tiene relación con Courses
user = User.query.filter_by(role='admin').first()
if user:
    # Debe tener atributo courses_dictated
    cursos = user.courses_dictated
    print(f"✅ User.courses_dictated funciona: {len(cursos)} cursos")
    
    # Debe tener atributo advisor_links
    links = user.advisor_links
    print(f"✅ User.advisor_links funciona: {len(links)} vínculos")
else:
    print("❌ No hay usuarios admin en la BD")
```

## 3. Validación de Relaciones en Course

```python
# Test: Course tiene relaciones múltiples
curso = Course.query.first()
if curso:
    # Debe tener instructor (backref)
    profesor = curso.instructor
    print(f"✅ Course.instructor funciona: {profesor.email if profesor else 'None'}")
    
    # Debe tener enrollments
    matrículas = curso.enrollments
    print(f"✅ Course.enrollments funciona: {len(matrículas)} matrículas")
    
    # Debe tener attendances
    asistencias = curso.attendances
    print(f"✅ Course.attendances funciona: {len(asistencias)} registros")
    
    # Debe tener alerts
    alertas = curso.alerts
    print(f"✅ Course.alerts funciona: {len(alertas)} alertas")
    
    # Debe tener advisor_links
    links = curso.advisor_links
    print(f"✅ Course.advisor_links funciona: {len(links)} vínculos")
else:
    print("❌ No hay cursos en la BD")
```

## 4. Validación de Relaciones en Student

```python
# Test: Student tiene relaciones múltiples
estudiante = Student.query.first()
if estudiante:
    # Debe tener enrollments
    matrículas = estudiante.enrollments
    print(f"✅ Student.enrollments funciona: {len(matrículas)} matrículas")
    
    # Debe tener attendances
    asistencias = estudiante.attendances
    print(f"✅ Student.attendances funciona: {len(asistencias)} asistencias")
    
    # Debe tener alerts
    alertas = estudiante.alerts
    print(f"✅ Student.alerts funciona: {len(alertas)} alertas")
else:
    print("❌ No hay estudiantes en la BD")
```

## 5. Validación de Relaciones en Enrollment

```python
# Test: Enrollment tiene acceso bidireccional
matricula = Enrollment.query.first()
if matricula:
    # Acceso a Student
    estudiante = matricula.student
    print(f"✅ Enrollment.student funciona: {estudiante.first_name if estudiante else 'None'}")
    
    # Acceso a Course
    curso = matricula.course
    print(f"✅ Enrollment.course funciona: {curso.name if curso else 'None'}")
else:
    print("❌ No hay matrículas en la BD")
```

## 6. Validación de Relaciones en Attendance

```python
# Test: Attendance tiene acceso bidireccional
asistencia = Attendance.query.first()
if asistencia:
    # Acceso a Student
    estudiante = asistencia.student
    print(f"✅ Attendance.student funciona: {estudiante.first_name if estudiante else 'None'}")
    
    # Acceso a Course
    curso = asistencia.course
    print(f"✅ Attendance.course funciona: {curso.name if curso else 'None'}")
else:
    print("❌ No hay registros de asistencia en la BD")
```

## 7. Validación de Relaciones en Alert

```python
# Test: Alert tiene acceso bidireccional
alerta = Alert.query.first()
if alerta:
    # Acceso a Student
    estudiante = alerta.student
    print(f"✅ Alert.student funciona: {estudiante.first_name if estudiante else 'None'}")
    
    # Acceso a Course (puede ser None)
    curso = alerta.course
    print(f"✅ Alert.course funciona: {curso.name if curso else 'None (opcional)'}")
else:
    print("❌ No hay alertas en la BD")
```

## 8. Validación de Relaciones en AdvisorCourseLink

```python
# Test: AdvisorCourseLink tiene acceso bidireccional
vinculo = AdvisorCourseLink.query.first()
if vinculo:
    # Acceso a Course
    curso = vinculo.course
    print(f"✅ AdvisorCourseLink.course funciona: {curso.name if curso else 'None'}")
    
    # Acceso a User (advisor)
    asesor = vinculo.advisor_user
    print(f"✅ AdvisorCourseLink.advisor_user funciona: {asesor.email if asesor else 'None'}")
else:
    print("❌ No hay vínculos de asesor en la BD")
```

## 9. Validación de Cascada de Eliminación

```python
# Test: Eliminar un Course debe eliminar sus Enrollments, Attendances, etc.
# CUIDADO: Esta es una prueba destructiva

from datetime import date

# Crear datos de prueba
user = User.query.filter_by(role='admin').first()
if user and len(user.courses_dictated) > 0:
    curso_test = user.courses_dictated[0]
    curso_id = curso_test.id
    
    # Verificar que tiene datos relacionados
    print(f"Curso a eliminar: {curso_test.name}")
    print(f"  - Matrículas: {len(curso_test.enrollments)}")
    print(f"  - Asistencias: {len(curso_test.attendances)}")
    print(f"  - Alertas: {len(curso_test.alerts)}")
    
    # DESCOMENTAR SOLO SI QUIERES PROBAR ELIMINACIÓN
    # db.session.delete(curso_test)
    # db.session.commit()
    
    # Verificar que todo se eliminó
    # curso_verificar = Course.query.get(curso_id)
    # print(f"✅ Course eliminado: {curso_verificar is None}")
    
    # Verificar que Enrollments relacionados también se eliminaron
    # enrollments = Enrollment.query.filter_by(course_id=curso_id).all()
    # print(f"✅ Enrollments eliminados: {len(enrollments) == 0}")
else:
    print("❌ No hay cursos de prueba disponibles")
```

## 10. Validación de Foreign Keys en BD

```python
# Verifica que las Foreign Keys están registradas en la BD
import sqlalchemy as sa
from sqlalchemy import inspect

inspector = inspect(Course)
print("Foreign Keys en Course:")
for fk in inspector.foreign_keys:
    print(f"  - {fk.parent.name} → {fk.column.name}")

# Resultado esperado:
# Foreign Keys en Course:
#   - admin_id → users.id

inspector = inspect(Enrollment)
print("Foreign Keys en Enrollment:")
for fk in inspector.foreign_keys:
    print(f"  - {fk.parent.name} → {fk.column.name}")

# Resultado esperado:
# Foreign Keys en Enrollment:
#   - student_id → students.id
#   - course_id → courses.id
```

## 11. Script de Prueba Completo

```python
#!/usr/bin/env python
"""
Script completo de validación de modelos
Ejecución: python test_models.py
"""

from app import create_app, db
from app.models import (
    User, Course, Student, Enrollment, Attendance, Alert, AdvisorCourseLink
)

def test_models():
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("VALIDACIÓN DE MODELOS Y RELACIONES")
        print("="*60)
        
        # Test 1: User
        print("\n[1] Validando User...")
        user = User.query.filter_by(role='admin').first()
        if user:
            print(f"✅ User encontrado: {user.email}")
            print(f"   - courses_dictated: {len(user.courses_dictated)} cursos")
            print(f"   - advisor_links: {len(user.advisor_links)} vínculos")
        else:
            print("❌ No hay usuarios admin")
        
        # Test 2: Course
        print("\n[2] Validando Course...")
        curso = Course.query.first()
        if curso:
            print(f"✅ Course encontrado: {curso.name}")
            print(f"   - instructor: {curso.instructor.email if curso.instructor else 'None'}")
            print(f"   - enrollments: {len(curso.enrollments)}")
            print(f"   - attendances: {len(curso.attendances)}")
            print(f"   - alerts: {len(curso.alerts)}")
            print(f"   - advisor_links: {len(curso.advisor_links)}")
        else:
            print("❌ No hay cursos")
        
        # Test 3: Student
        print("\n[3] Validando Student...")
        estudiante = Student.query.first()
        if estudiante:
            print(f"✅ Student encontrado: {estudiante.first_name} {estudiante.last_name}")
            print(f"   - enrollments: {len(estudiante.enrollments)}")
            print(f"   - attendances: {len(estudiante.attendances)}")
            print(f"   - alerts: {len(estudiante.alerts)}")
        else:
            print("❌ No hay estudiantes")
        
        # Test 4: Enrollment
        print("\n[4] Validando Enrollment...")
        matricula = Enrollment.query.first()
        if matricula:
            print(f"✅ Enrollment encontrado")
            print(f"   - student: {matricula.student.first_name if matricula.student else 'None'}")
            print(f"   - course: {matricula.course.name if matricula.course else 'None'}")
        else:
            print("❌ No hay matrículas")
        
        # Test 5: Attendance
        print("\n[5] Validando Attendance...")
        asistencia = Attendance.query.first()
        if asistencia:
            print(f"✅ Attendance encontrado")
            print(f"   - student: {asistencia.student.first_name if asistencia.student else 'None'}")
            print(f"   - course: {asistencia.course.name if asistencia.course else 'None'}")
            print(f"   - status: {asistencia.status}")
        else:
            print("❌ No hay registros de asistencia")
        
        # Test 6: Alert
        print("\n[6] Validando Alert...")
        alerta = Alert.query.first()
        if alerta:
            print(f"✅ Alert encontrada")
            print(f"   - student: {alerta.student.first_name if alerta.student else 'None'}")
            print(f"   - course: {alerta.course.name if alerta.course else 'None (opcional)'}")
        else:
            print("❌ No hay alertas")
        
        # Test 7: AdvisorCourseLink
        print("\n[7] Validando AdvisorCourseLink...")
        vinculo = AdvisorCourseLink.query.first()
        if vinculo:
            print(f"✅ AdvisorCourseLink encontrado")
            print(f"   - course: {vinculo.course.name if vinculo.course else 'None'}")
            print(f"   - advisor_user: {vinculo.advisor_user.email if vinculo.advisor_user else 'None'}")
            print(f"   - status: {vinculo.status}")
        else:
            print("❌ No hay vínculos de asesor")
        
        print("\n" + "="*60)
        print("VALIDACIÓN COMPLETADA")
        print("="*60)

if __name__ == '__main__':
    test_models()
```

## 12. Validación SQL Directa

```sql
-- Ejecutar en Supabase para verificar Foreign Keys

-- Ver todas las FK en la BD
SELECT
    t.tablename,
    constraint_name,
    src_column,
    target_table,
    target_column
FROM (
    SELECT
        t.tablename,
        kcu.constraint_name,
        kcu.column_name AS src_column,
        ccu.table_name AS target_table,
        ccu.column_name AS target_column
    FROM information_schema.table_constraints AS t
    JOIN information_schema.key_column_usage AS kcu
        ON t.constraint_name = kcu.constraint_name
        AND t.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = t.constraint_name
        AND ccu.table_schema = t.table_schema
    WHERE t.constraint_type = 'FOREIGN KEY'
) AS t
ORDER BY tablename;

-- Resultado esperado:
-- courses    | fk_admin_id              | admin_id        | users       | id
-- enrollments| fk_student_id            | student_id      | students    | id
-- enrollments| fk_course_id             | course_id       | courses     | id
-- attendance | fk_student_id            | student_id      | students    | id
-- attendance | fk_course_id             | course_id       | courses     | id
-- alerts     | fk_student_id            | student_id      | students    | id
-- alerts     | fk_course_id             | course_id       | courses     | id
-- advisor_course_links | fk_course_id   | course_id       | courses     | id
-- advisor_course_links | fk_advisor_id  | advisor_user_id | users       | id
```

## Checklist de Validación

- [ ] ✅ User tiene atributo `courses_dictated`
- [ ] ✅ User tiene atributo `advisor_links`
- [ ] ✅ Course tiene atributo `instructor` (backref)
- [ ] ✅ Course tiene atributo `enrollments`
- [ ] ✅ Course tiene atributo `attendances`
- [ ] ✅ Course tiene atributo `alerts`
- [ ] ✅ Course tiene atributo `advisor_links`
- [ ] ✅ Student tiene atributo `enrollments`
- [ ] ✅ Student tiene atributo `attendances`
- [ ] ✅ Student tiene atributo `alerts`
- [ ] ✅ Enrollment tiene acceso a `student` y `course`
- [ ] ✅ Attendance tiene acceso a `student` y `course`
- [ ] ✅ Alert tiene acceso a `student` y `course`
- [ ] ✅ AdvisorCourseLink tiene acceso a `course` y `advisor_user`
- [ ] ✅ Todas las Foreign Keys existen en PostgreSQL
- [ ] ✅ Cascade delete funciona correctamente

---

**Si todos estos tests pasan, tus modelos están correctamente configurados.** ✅
