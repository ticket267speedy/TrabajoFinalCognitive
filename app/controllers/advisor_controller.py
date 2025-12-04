from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User
from ..services.advisor_service import AdvisorService
from functools import wraps

advisor_bp = Blueprint("advisor", __name__)
advisor_service = AdvisorService()

# ==================== VISTAS ====================

def advisor_required(f):
    """Decorador para proteger vistas que requieren rol advisor (cliente)"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        
        try:
            # Convertir a int si es necesario
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                pass
            
            user = User.query.get(user_id)
            if not user:
                return redirect(url_for('shared.login_view'))
            
            # Verificar rol (advisor o client ambos pueden acceder)
            role_value = user.role if not hasattr(user.role, 'value') else user.role.value
            if role_value not in ['advisor', 'client']:
                return redirect(url_for('shared.login_view'))
        except Exception as e:
            print(f"Error en advisor_required: {str(e)}")
            return redirect(url_for('shared.login_view'))
        
        return f(*args, **kwargs)
    return decorated

@advisor_bp.get("/")
def advisor_dashboard_view():
    """Vista del dashboard del asesor de becas (no requiere JWT, redirige al cliente)"""
    return render_template("advisor/dashboard.html")

@advisor_bp.get("/students")
def client_students_view():
    """Vista de estudiantes becarios para el cliente"""
    return render_template("client/students.html")

@advisor_bp.get("/courses")
def client_courses_view():
    """Vista de cursos para el cliente"""
    return render_template("client/courses.html")

@advisor_bp.get("/profile")
@advisor_bp.get("/profile")
def client_profile_view():
    """Vista de perfil para el cliente"""
    return render_template("client/profile.html")
# ==================== API ENDPOINTS ====================

@advisor_bp.get("/api/students")
@jwt_required()
def get_advisor_students():
    """Obtener estudiantes becarios para el asesor"""
    user_id = get_jwt_identity()
    
    # Validar rol
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        user_id_int = user_id
    
    user = User.query.get(user_id_int)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    role_value = user.role if not hasattr(user.role, 'value') else user.role.value
    if role_value not in ['advisor', 'client']:
        return jsonify({"error": "No autorizado"}), 403
    
    # Usar servicio para obtener becarios
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    result = advisor_service.get_scholarship_students(limit=limit, offset=offset)
    
    if not result["ok"]:
        return jsonify({"error": result.get("message")}), 500
    
    return jsonify(result)

@advisor_bp.get("/api/alerts")
@jwt_required()
def get_advisor_alerts():
    """Obtener alertas para el asesor"""
    user_id = get_jwt_identity()
    
    # Validar rol
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        user_id_int = user_id
    
    user = User.query.get(user_id_int)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    role_value = user.role if not hasattr(user.role, 'value') else user.role.value
    if role_value not in ['advisor', 'client']:
        return jsonify({"error": "No autorizado"}), 403
    
    # Usar servicio para obtener alertas
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    result = advisor_service.get_alerts(limit=limit, offset=offset)
    
    if not result["ok"]:
        return jsonify({"error": result.get("message")}), 500
    
    return jsonify(result)

@advisor_bp.patch("/api/alerts/<int:alert_id>/read")
@jwt_required()
def mark_alert_as_read(alert_id):
    """Marcar alerta como leída"""
    user_id = get_jwt_identity()
    
    # Validar rol
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        user_id_int = user_id
    
    user = User.query.get(user_id_int)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    role_value = user.role if not hasattr(user.role, 'value') else user.role.value
    if role_value not in ['advisor', 'client']:
        return jsonify({"error": "No autorizado"}), 403
    
    # Usar servicio para marcar como leída
    result = advisor_service.mark_alert_as_read(alert_id)
    
    if not result["ok"]:
        return jsonify({"error": result.get("message")}), 404
    
    return jsonify(result)

@advisor_bp.get("/api/summary")
@jwt_required()
def get_advisor_summary():
    """Obtener resumen de estadísticas para el asesor"""
    user_id = get_jwt_identity()
    
    # Validar rol
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        user_id_int = user_id
    
    user = User.query.get(user_id_int)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    role_value = user.role if not hasattr(user.role, 'value') else user.role.value
    if role_value not in ['advisor', 'client']:
        return jsonify({"error": "No autorizado"}), 403
    
    # Usar servicio para obtener resumen
    result = advisor_service.get_summary()
    
    if not result["ok"]:
        return jsonify({"error": result.get("message")}), 500
    
    return jsonify(result["data"])