from flask import Blueprint, render_template, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import check_password_hash
from ..extensions import db
from ..models import User, Course, Student, Enrollment

shared_bp = Blueprint("shared", __name__)

# ==================== VISTAS COMPARTIDAS ====================

@shared_bp.get("/")
def root_view():
    """Redirige la ruta raíz al login para evitar 404."""
    return redirect("/login")

@shared_bp.get("/login")
def login_view():
    """Vista de login general"""
    return render_template("shared/login.html")

@shared_bp.get("/register")
def register_view():
    """Vista de registro (solo para asesores)"""
    return render_template("shared/register.html")

@shared_bp.get("/forgot-password")
def forgot_password_view():
    """Vista de recuperar contraseña"""
    return render_template("shared/forgot_password.html")

@shared_bp.get("/course/<int:course_id>/people")
def course_people_view(course_id: int):
    """Vista de personas del curso (profesor y becarios)"""
    return render_template("shared/course_people.html", course_id=course_id)

# ==================== API ENDPOINTS COMPARTIDOS ====================

# Nota: el login de API se gestiona en el blueprint `api` con la ruta
# `POST /api/login` (universal_login) usando `silent=True` al decodificar JSON
# para evitar errores 400 por payload mal citado en PowerShell.
# Aquí no se define un duplicado para prevenir conflictos de rutas.

@shared_bp.get("/api/users/<int:user_id>/profile")
@jwt_required()
def get_user_profile(user_id):
    """Obtener perfil público de cualquier usuario (requiere autenticación)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "Usuario no autenticado"}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Obtener cursos si es admin/profesor
        courses_data = []
        if user.role == 'admin':
            courses = Course.query.filter_by(admin_id=user.id).all()
            courses_data = [{"id": c.id, "name": c.name} for c in courses]
        
        return jsonify({
            "id": user.id,
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "description": user.description or "",
            "profile_photo_url": user.profile_photo_url,
            "courses": courses_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@shared_bp.get("/api/courses/<int:course_id>/people")
@jwt_required()
def get_course_people(course_id):
    """Obtener profesor y estudiantes becarios de un curso"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "Usuario no autenticado"}), 401
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Curso no encontrado"}), 404
        
        # Obtener profesor del curso
        professor = User.query.get(course.admin_id)
        professor_data = None
        if professor:
            professor_data = {
                "id": professor.id,
                "first_name": professor.first_name,
                "last_name": professor.last_name,
                "description": professor.description or "",
                "profile_photo_url": professor.profile_photo_url
            }
        
        # Obtener estudiantes becarios matriculados
        students = db.session.query(Student).join(Enrollment).filter(
            Enrollment.course_id == course_id,
            Student.is_scholarship_student == True
        ).all()
        
        students_data = []
        for student in students:
            students_data.append({
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email
            })
        
        return jsonify({
            "course": {
                "id": course.id,
                "name": course.name
            },
            "professor": professor_data,
            "students": students_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500