from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, Course, Student, Enrollment, Alert
from sqlalchemy import desc

advisor_bp = Blueprint("advisor", __name__)

# ==================== VISTAS ====================

@advisor_bp.get("/")
def advisor_dashboard_view():
    """Vista del dashboard del asesor de becas"""
    return render_template("advisor/dashboard.html")

# ==================== API ENDPOINTS ====================

@advisor_bp.get("/api/students")
@jwt_required()
def get_advisor_students():
    """Obtener estudiantes becarios para el asesor"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'advisor':
            return jsonify({"error": "No autorizado"}), 403
        
        # Solo estudiantes becarios
        students = Student.query.filter_by(is_scholarship_student=True).all()
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

@advisor_bp.get("/api/alerts")
@jwt_required()
def get_advisor_alerts():
    """Obtener alertas para el asesor"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'advisor':
            return jsonify({"error": "No autorizado"}), 403
        
        # Obtener alertas ordenadas por fecha (más recientes primero)
        alerts = Alert.query.order_by(desc(Alert.created_at)).all()
        alerts_data = []
        
        for alert in alerts:
            student = Student.query.get(alert.student_id)
            course = Course.query.get(alert.course_id) if alert.course_id else None
            
            alert_data = {
                "id": alert.id,
                "message": alert.message,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
                "is_read": alert.is_read,
                "student": {
                    "id": student.id,
                    "first_name": student.first_name,
                    "last_name": student.last_name
                } if student else None
            }
            
            if course:
                alert_data["course_id"] = course.id
                alert_data["course_name"] = course.name
            
            alerts_data.append(alert_data)
        
        return jsonify(alerts_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@advisor_bp.patch("/api/alerts/<int:alert_id>/read")
@jwt_required()
def mark_alert_as_read(alert_id):
    """Marcar alerta como leída"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'advisor':
            return jsonify({"error": "No autorizado"}), 403
        
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({"error": "Alerta no encontrada"}), 404
        
        alert.is_read = True
        db.session.commit()
        
        return jsonify({"message": "Alerta marcada como leída"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@advisor_bp.get("/api/summary")
@jwt_required()
def get_advisor_summary():
    """Obtener resumen de estadísticas para el asesor"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id
        user = User.query.get(user_id_int)
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        if not user or role_value != 'advisor':
            return jsonify({"error": "No autorizado"}), 403
        
        # Contar estudiantes becarios
        total_scholarship_students = Student.query.filter_by(is_scholarship_student=True).count()
        
        # Contar alertas no leídas
        unread_alerts = Alert.query.filter_by(is_read=False).count()
        
        # Contar cursos con becarios
        courses_with_scholars = db.session.query(Course.id).join(Enrollment).join(Student).filter(
            Student.is_scholarship_student == True
        ).distinct().count()
        
        return jsonify({
            "total_scholarship_students": total_scholarship_students,
            "unread_alerts": unread_alerts,
            "courses_with_scholars": courses_with_scholars
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500