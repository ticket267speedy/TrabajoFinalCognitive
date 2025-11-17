#!/usr/bin/env python3
"""Script para actualizar la base de datos con datos mock usando Flask-SQLAlchemy"""

import os
import sys
from datetime import datetime, timedelta

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Student, Course, Enrollment, Alert

def update_database():
    """Ejecuta la actualización de la base de datos con datos mock"""
    app = create_app()
    
    with app.app_context():
        # Asegurar que el esquema existe en entornos locales (SQLite)
        # En caso de incompatibilidad con migraciones (p.e. ALTER ENUM en SQLite),
        # creamos las tablas a partir de los modelos.
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️ No se pudo crear el esquema automáticamente: {e}")
        try:
            # Limpiar datos existentes
            print("🧹 Limpiando datos existentes...")
            Alert.query.delete()
            Enrollment.query.delete()
            Course.query.delete()
            Student.query.delete()
            User.query.delete()
            db.session.commit()
            
            # Crear usuarios
            print("👥 Creando usuarios...")
            users = [
                User(
                    id=1,
                    email='asesor@demo.com',
                    password_text='Password123',
                    first_name='Ana',
                    last_name='Asesora',
                    role='advisor',
                    description='Asesora de becas con experiencia en seguimiento académico'
                ),
                User(
                    id=2,
                    email='cliente@demo.com',
                    password_text='Password123',
                    first_name='Carlos',
                    last_name='Cliente',
                    role='client'
                ),
                User(
                    id=3,
                    email='admin@demo.com',
                    password_text='Password123',
                    first_name='Elmer',
                    last_name='Arellanos',
                    role='admin',
                    description='Profesor de Ingeniería Eléctrica con más de 15 años de experiencia en circuitos y sistemas digitales'
                )
            ]
            
            for user in users:
                db.session.add(user)
            db.session.commit()
            
            # Crear estudiantes
            print("🎓 Creando estudiantes...")
            students = [
                Student(
                    id=1,
                    first_name='Felipe',
                    last_name='García',
                    email='felipe@example.com',
                    is_scholarship_student=True
                ),
                Student(
                    id=2,
                    first_name='Franco',
                    last_name='Pérez',
                    email='franco@example.com',
                    is_scholarship_student=True
                ),
                Student(
                    id=3,
                    first_name='Israel',
                    last_name='López',
                    email='israel@example.com',
                    is_scholarship_student=False
                ),
                # Nuevos estudiantes mock
                Student(
                    id=4,
                    first_name='María',
                    last_name='Rojas',
                    email='maria@example.com',
                    is_scholarship_student=False
                ),
                Student(
                    id=5,
                    first_name='Juan',
                    last_name='Torres',
                    email='juan@example.com',
                    is_scholarship_student=True
                ),
                Student(
                    id=6,
                    first_name='Lucía',
                    last_name='Vega',
                    email='lucia@example.com',
                    is_scholarship_student=True
                ),
                Student(
                    id=7,
                    first_name='Pedro',
                    last_name='Ruiz',
                    email='pedro@example.com',
                    is_scholarship_student=False
                ),
            ]
            
            for student in students:
                db.session.add(student)
            db.session.commit()
            
            # Crear cursos
            print("📚 Creando cursos...")
            courses = [
                Course(id=1, name='Circuitos Eléctricos', admin_id=3),
                Course(id=2, name='Circuitos Eléctricos y Electrónicos I', admin_id=3),
                Course(id=3, name='Circuitos Digitales', admin_id=3)
            ]
            
            for course in courses:
                db.session.add(course)
            db.session.commit()
            
            # Crear matrículas
            print("📝 Creando matrículas...")
            enrollments = [
                Enrollment(id=1, student_id=1, course_id=1),  # Felipe en Circuitos Eléctricos
                Enrollment(id=2, student_id=2, course_id=1),  # Franco en Circuitos Eléctricos
                Enrollment(id=3, student_id=1, course_id=2),  # Felipe en Circuitos Eléctricos y Electrónicos I
                Enrollment(id=4, student_id=2, course_id=3),  # Franco en Circuitos Digitales
                Enrollment(id=5, student_id=1, course_id=3),  # Felipe en Circuitos Digitales
                # Nuevas matrículas
                Enrollment(id=6, student_id=3, course_id=2),  # Israel en Circuitos Eléctricos y Electrónicos I
                Enrollment(id=7, student_id=4, course_id=1),  # María en Circuitos Eléctricos
                Enrollment(id=8, student_id=5, course_id=2),  # Juan en Circuitos Eléctricos y Electrónicos I
                Enrollment(id=9, student_id=6, course_id=3),  # Lucía en Circuitos Digitales
                Enrollment(id=10, student_id=7, course_id=1)  # Pedro en Circuitos Eléctricos
            ]
            
            for enrollment in enrollments:
                db.session.add(enrollment)
            db.session.commit()
            
            # Crear alertas
            print("🚨 Creando alertas...")
            alerts = [
                Alert(
                    id=1,
                    course_id=1,
                    student_id=1,
                    message='Felipe García ha faltado 3 veces consecutivas',
                    is_read=False,
                    created_at=datetime.now() - timedelta(days=2)
                ),
                Alert(
                    id=2,
                    course_id=2,
                    student_id=1,
                    message='Felipe García tiene bajo rendimiento en evaluaciones',
                    is_read=False,
                    created_at=datetime.now() - timedelta(days=1)
                ),
                Alert(
                    id=3,
                    course_id=3,
                    student_id=2,
                    message='Franco Pérez necesita apoyo adicional en laboratorio',
                    is_read=True,
                    created_at=datetime.now() - timedelta(days=3)
                )
            ]
            
            for alert in alerts:
                db.session.add(alert)
            db.session.commit()
            
            print("✅ Base de datos actualizada correctamente con datos mock")
            print(f"   - {len(users)} usuarios creados")
            print(f"   - {len(students)} estudiantes creados")
            print(f"   - {len(courses)} cursos creados")
            print(f"   - {len(enrollments)} matrículas creadas")
            print(f"   - {len(alerts)} alertas creadas")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar la base de datos: {e}")
            return False

if __name__ == "__main__":
    update_database()