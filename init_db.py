"""
Script para inicializar la base de datos con datos de ejemplo.
Ejecuta con: python init_db.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Agregar el path para importar la app
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import User, Student, Course, Enrollment
from werkzeug.security import generate_password_hash

print("=" * 60)
print("🗄️  INICIALIZANDO BASE DE DATOS")
print("=" * 60)

app = create_app()

with app.app_context():
    print("\n1️⃣  Creando tablas...")
    try:
        db.create_all()
        print("   ✅ Tablas creadas correctamente")
    except Exception as e:
        print(f"   ⚠️  Tablas ya existen o error: {str(e)[:100]}")

    print("\n2️⃣  Verificando datos de ejemplo...")
    
    # Verificar si ya existen datos
    admin_count = User.query.filter_by(role="admin").count()
    if admin_count > 0:
        print("   ℹ️  Base de datos ya tiene datos. Skipping...")
        print(f"   📊 Usuarios admin existentes: {admin_count}")
        print(f"   📊 Estudiantes: {Student.query.count()}")
        print(f"   📊 Cursos: {Course.query.count()}")
    else:
        print("   ➕ Agregando datos de ejemplo...")
        
        try:
            # Crear admin (profesor)
            admin = User(
                email="admin@demo.com",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                first_name="Profesor",
                last_name="Admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("   ✅ Admin creado: admin@demo.com / admin123")
            
            # Crear estudiantes de ejemplo
            students_data = [
                {"first_name": "María", "last_name": "Rojas", "email": "maria@example.com", "is_scholarship": False},
                {"first_name": "Juan", "last_name": "Torres", "email": "juan@example.com", "is_scholarship": True},
                {"first_name": "Felipe", "last_name": "García", "email": "felipe@example.com", "is_scholarship": False},
                {"first_name": "Israel", "last_name": "Carlos", "email": "israel@example.com", "is_scholarship": False},
                {"first_name": "Franco", "last_name": "Pérez", "email": "franco@example.com", "is_scholarship": False},
            ]
            
            for s_data in students_data:
                student = Student(
                    first_name=s_data["first_name"],
                    last_name=s_data["last_name"],
                    email=s_data["email"],
                    is_scholarship_student=s_data["is_scholarship"]
                )
                db.session.add(student)
            db.session.commit()
            print(f"   ✅ {len(students_data)} estudiantes creados")
            
            # Crear cursos
            courses_data = [
                {"name": "Programación I", "admin_id": admin.id},
                {"name": "Bases de Datos", "admin_id": admin.id},
                {"name": "Desarrollo Web", "admin_id": admin.id},
            ]
            
            for c_data in courses_data:
                course = Course(
                    name=c_data["name"],
                    admin_id=c_data["admin_id"]
                )
                db.session.add(course)
            db.session.commit()
            print(f"   ✅ {len(courses_data)} cursos creados")
            
            # Crear enrollments
            students = Student.query.all()
            courses = Course.query.all()
            
            for i, student in enumerate(students):
                course = courses[i % len(courses)]
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id
                )
                db.session.add(enrollment)
            db.session.commit()
            print(f"   ✅ Estudiantes inscritos en cursos")
            
        except Exception as e:
            print(f"   ❌ Error al agregar datos: {str(e)}")
            db.session.rollback()

print("\n" + "=" * 60)
print("✅ BASE DE DATOS INICIALIZADA")
print("=" * 60)
print("\n📝 Credenciales de prueba:")
print("   Email: admin@demo.com")
print("   Password: admin123")
