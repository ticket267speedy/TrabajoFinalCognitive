from flask import Blueprint, render_template, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import User, Course, Student, Enrollment
import os

admin_bp = Blueprint("admin", __name__)

# ==================== VISTAS ====================

@admin_bp.get("/login")
def admin_login_view():
    """Redirige al login único"""
    return redirect("/login")

@admin_bp.get("/")
def admin_dashboard_view():
    """Vista del dashboard principal del administrador"""
    return render_template("admin/admin_dashboard.html")

@admin_bp.get("/profile")
def admin_profile_view():
    """Vista del perfil del administrador"""
    return render_template("admin/admin_profile.html")

@admin_bp.get("/course/<int:course_id>/session")
def admin_course_session_view(course_id: int):
    """Vista de sesión activa por curso para el administrador.

    Muestra la lista de alumnos y controles de cámara/registro manual.
    """
    return render_template("admin/session_active.html", course_id=course_id)

# ==================== API ENDPOINTS ====================

@admin_bp.get("/api/profile")
@jwt_required()
def get_admin_profile():
    """Obtener perfil del administrador autenticado"""
    try:
        user_id = get_jwt_identity()
        # Asegurar que el ID sea entero
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        # Normalizar rol para soportar Enum o string
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        # Obtener cursos que dicta el administrador
        courses = Course.query.filter_by(admin_id=user.id).all()
        courses_data = [{"id": c.id, "name": c.name} for c in courses]
        
        return jsonify({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "description": user.description or "",
            "profile_photo_url": user.profile_photo_url,
            "courses": courses_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.patch("/api/profile")
@jwt_required()
def update_admin_profile():
    """Actualizar descripción del perfil del administrador"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        description = data.get('description', '').strip()
        
        # Validar límite de 1000 caracteres
        if len(description) > 1000:
            return jsonify({"error": "La descripción no puede exceder 1000 caracteres"}), 400
        
        user.description = description
        db.session.commit()
        
        return jsonify({"message": "Perfil actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.post("/api/profile/photo")
@jwt_required()
def upload_admin_photo():
    """Subir foto de perfil del administrador"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        if 'photo' not in request.files:
            return jsonify({"error": "No se encontró archivo de foto"}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó archivo"}), 400
        
        # Validar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({"error": "Tipo de archivo no permitido"}), 400
        
        # Guardar archivo
        filename = secure_filename(f"admin_{user_id}_{file.filename}")
        upload_folder = os.path.join('app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Actualizar URL en base de datos
        user.profile_photo_url = f"/static/uploads/{filename}"
        db.session.commit()
        
        return jsonify({
            "message": "Foto subida correctamente",
            "profile_photo_url": user.profile_photo_url
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.get("/api/students")
@jwt_required()
def get_students():
    """Obtener lista de estudiantes con filtros"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        # Parámetros de filtro
        scholarship_param = request.args.get('scholarship', '').lower()
        
        query = Student.query
        
        # Filtro por beca
        if scholarship_param:
            if scholarship_param in ['true', '1', 'yes', 'si']:
                query = query.filter(Student.is_scholarship_student == True)
            elif scholarship_param in ['false', '0', 'no']:
                query = query.filter(Student.is_scholarship_student == False)
        
        students = query.all()
        students_data = []
        
        for student in students:
            students_data.append({
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "is_scholarship_student": student.is_scholarship_student
            })
        
        return jsonify(students_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.get("/api/courses")
@jwt_required()
def get_admin_courses():
    """Obtener cursos del administrador"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        courses = Course.query.filter_by(admin_id=user.id).all()
        courses_data = []
        
        for course in courses:
            # Contar estudiantes becarios matriculados
            scholarship_count = db.session.query(Enrollment).join(Student).filter(
                Enrollment.course_id == course.id,
                Student.is_scholarship_student == True
            ).count()
            
            courses_data.append({
                "id": course.id,
                "name": course.name,
                "scholarship_students_count": scholarship_count
            })
        
        return jsonify(courses_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500