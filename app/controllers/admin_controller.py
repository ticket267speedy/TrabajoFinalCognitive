from flask import Blueprint, render_template, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import User, Course, Student, Enrollment, Attendance
import os
from datetime import datetime, date

admin_bp = Blueprint("admin", __name__)
admin_api_bp = Blueprint("admin_api", __name__)

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

@admin_bp.get("/courses")
def courses_list_view():
    """Vista de listado de cursos"""
    return render_template("admin/courses_list.html")

@admin_bp.get("/courses/create")
def courses_create_view():
    """Vista de crear nuevo curso"""
    return render_template("admin/courses_create.html")

@admin_bp.get("/courses/<int:course_id>/edit")
def courses_edit_view(course_id: int):
    """Vista de editar curso"""
    return render_template("admin/courses_edit.html", course_id=course_id)

@admin_bp.get("/courses/<int:course_id>/delete")
def courses_delete_view(course_id: int):
    """Vista de eliminar curso"""
    return render_template("admin/courses_delete.html", course_id=course_id)

@admin_bp.get("/courses/<int:course_id>/students")
def course_students_view(course_id: int):
    """Vista de estudiantes del curso"""
    return render_template("admin/course_students.html", course_id=course_id)

@admin_bp.get("/students")
def students_view():
    """Vista de listado de estudiantes"""
    return render_template("admin/students.html")

@admin_bp.get("/class-session")
def class_session_view():
    """Vista de sesiones de clase"""
    return render_template("admin/class-session.html")

@admin_bp.get("/attendance")
def attendance_view():
    """Vista de resumen de asistencia"""
    return render_template("admin/attendance.html")

# ==================== API ENDPOINTS ====================

@admin_api_bp.get("/admin/profile")
@jwt_required()
def get_admin_profile():
    """Obtener perfil del administrador autenticado"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        # Obtener cursos que dicta el administrador
        courses = Course.query.filter_by(admin_id=user.id).all()
        courses_data = [{"id": c.id, "name": c.name} for c in courses]
        
        return jsonify({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "profile_photo_url": user.profile_photo_url,
            "role": role_value,
            "courses": courses_data
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_bp.patch("/api/profile")
@jwt_required()
def update_admin_profile():
    """Actualizar perfil del administrador"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'first_name' in data:
            user.first_name = data.get('first_name', '').strip()[:100]
        if 'last_name' in data:
            user.last_name = data.get('last_name', '').strip()[:100]
        
        db.session.commit()
        return jsonify({"message": "Perfil actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
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
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
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
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_api_bp.get("/admin/students")
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
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
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
            # Obtener cursos en los que está matriculado
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()
            course_names = [Course.query.get(e.course_id).name for e in enrollments if Course.query.get(e.course_id)]
            
            students_data.append({
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "is_scholarship_student": student.is_scholarship_student,
                "profile_photo_url": student.profile_photo_url,
                "courses": course_names
            })
        
        return jsonify({"data": students_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_api_bp.get("/admin/courses")
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
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        courses = Course.query.filter_by(admin_id=user.id).all()
        courses_data = []
        
        for course in courses:
            try:
                # Contar estudiantes matriculados
                enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
                
                courses_data.append({
                    "id": course.id,
                    "name": course.name,
                    "start_time": str(course.start_time) if course.start_time else None,
                    "end_time": str(course.end_time) if course.end_time else None,
                    "days_of_week": course.days_of_week,
                    "students_count": enrollment_count
                })
            except Exception as course_error:
                print(f"Error procesando curso {course.id}: {course_error}")
                continue
        
        return jsonify({"data": courses_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_api_bp.get("/admin/metrics")
@jwt_required()
def get_admin_metrics():
    """Obtener métricas generales del dashboard"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        # Contar estudiantes totales
        total_students = Student.query.count()
        
        # Contar cursos del admin
        total_courses = Course.query.filter_by(admin_id=user.id).count()
        
        # Contar matriculaciones totales en cursos del admin
        total_enrollments = db.session.query(Enrollment).join(Course).filter(
            Course.admin_id == user.id
        ).count()
        
        # Calcular asistencia promedio de hoy
        today = date.today()
        today_attendance = db.session.query(Attendance).filter(
            Attendance.date == today,
            Attendance.status.in_(['presente', 'tardanza'])
        ).count()
        
        total_today_records = db.session.query(Attendance).filter(
            Attendance.date == today
        ).count()
        
        attendance_today = round((today_attendance / total_today_records * 100), 1) if total_today_records > 0 else 0
        
        # Obtener nombres de cursos del admin
        course_names = [c.name for c in Course.query.filter_by(admin_id=user.id).limit(5).all()]
        
        # Preparar datos de respuesta
        response_data = {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "attendance_today": attendance_today,
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            "attendance_data": [80, 82, 85, 83, 87, 90],
            "course_names": course_names if course_names else ["Sin cursos"],
            "course_students": [10, 15, 12, 8, 20][:max(len(course_names), 1)]
        }
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_api_bp.get("/admin/attendance")
@jwt_required()
def get_admin_attendance():
    """Obtener registros de asistencia del admin"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        # Obtener asistencias de los cursos del admin
        attendance_records = db.session.query(Attendance).join(Course).filter(
            Course.admin_id == user.id
        ).order_by(Attendance.date.desc()).limit(50).all()
        
        attendance_data = []
        for record in attendance_records:
            try:
                student = Student.query.get(record.student_id)
                course = Course.query.get(record.course_id)
                attendance_data.append({
                    "id": record.id,
                    "student_name": f"{student.first_name} {student.last_name}" if student else "Unknown",
                    "course_name": course.name if course else "Unknown",
                    "date": record.date.isoformat(),
                    "entry_time": str(record.entry_time) if record.entry_time else None,
                    "exit_time": str(record.exit_time) if record.exit_time else None,
                    "status": record.status
                })
            except Exception as att_error:
                print(f"Error procesando asistencia {record.id}: {att_error}")
                continue
        
        return jsonify({"data": attendance_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_api_bp.get("/admin/courses/<int:course_id>/students")
@jwt_required()
def get_course_students(course_id: int):
    """Obtener estudiantes matriculados en un curso específico"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        # Verificar que el curso pertenece al admin
        course = Course.query.get(course_id)
        if not course or course.admin_id != user.id:
            return jsonify({"error": "Curso no encontrado o no autorizado"}), 404
        
        # Obtener estudiantes matriculados
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        students_data = []
        
        for enrollment in enrollments:
            student = Student.query.get(enrollment.student_id)
            if student:
                students_data.append({
                    "id": student.id,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "email": student.email,
                    "is_scholarship_student": student.is_scholarship_student
                })
        
        return jsonify({"data": students_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_api_bp.get("/admin/courses/<int:course_id>/attendance")
@jwt_required()
def get_course_attendance(course_id: int):
    """Obtener asistencia de un curso específico"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        # Verificar que el curso pertenece al admin
        course = Course.query.get(course_id)
        if not course or course.admin_id != user.id:
            return jsonify({"error": "Curso no encontrado o no autorizado"}), 404
        
        # Obtener registros de asistencia del curso (hoy)
        from datetime import date
        today = date.today()
        attendance_records = Attendance.query.filter_by(course_id=course_id).filter(
            Attendance.date == today
        ).all()
        
        attendance_data = []
        for record in attendance_records:
            try:
                student = Student.query.get(record.student_id)
                attendance_data.append({
                    "id": record.id,
                    "student_id": record.student_id,
                    "student_name": f"{student.first_name} {student.last_name}" if student else "Unknown",
                    "entry_time": str(record.entry_time) if record.entry_time else None,
                    "exit_time": str(record.exit_time) if record.exit_time else None,
                    "status": record.status,
                    "date": record.date.isoformat()
                })
            except Exception as att_error:
                print(f"Error procesando asistencia {record.id}: {att_error}")
                continue
        
        return jsonify({"data": attendance_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@admin_api_bp.patch("/admin/attendance/<int:attendance_id>")
@jwt_required()
def update_attendance(attendance_id: int):
    """Actualizar estado de asistencia"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if role_value != 'admin':
            return jsonify({"error": "No autorizado"}), 403
        
        attendance = Attendance.query.get(attendance_id)
        if not attendance:
            return jsonify({"error": "Registro de asistencia no encontrado"}), 404
        
        # Verificar que el curso pertenece al admin
        course = Course.query.get(attendance.course_id)
        if not course or course.admin_id != user.id:
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        if 'status' in data:
            valid_statuses = ['presente', 'tardanza', 'falta', 'salida_repentina']
            if data.get('status') not in valid_statuses:
                return jsonify({"error": f"Status debe ser uno de: {','.join(valid_statuses)}"}), 400
            attendance.status = data.get('status')
        
        if 'entry_time' in data:
            attendance.entry_time = data.get('entry_time')
        
        if 'exit_time' in data:
            attendance.exit_time = data.get('exit_time')
        
        db.session.commit()
        return jsonify({"message": "Asistencia actualizada"}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
