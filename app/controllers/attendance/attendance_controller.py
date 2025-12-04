"""
Controlador de Asistencia

Gestiona todas las rutas relacionadas con asistencia:
- Registro de asistencia
- Consulta de registro
- Estadísticas de asistencia
- Alertas por inasistencia
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any, Optional
from datetime import date

from ...services.attendance_service import AttendanceService
from ...extensions import db

# Blueprint para rutas de asistencia
attendance_bp = Blueprint(
    'attendance',
    __name__,
    url_prefix='/api/attendance'
)

# Instancia del servicio
attendance_service = AttendanceService()


# ==================== RUTAS DE ASISTENCIA ====================

@attendance_bp.post('/mark')
@jwt_required()
def mark_attendance() -> tuple[Dict[str, Any], int]:
    """
    Marca la asistencia de un estudiante.
    
    Body JSON:
    {
        "student_id": int,
        "course_id": int,
        "status": "presente|tardanza|falta|salida_repentina",
        "entry_time": "HH:MM:SS" (opcional),
        "exit_time": "HH:MM:SS" (opcional),
        "attendance_date": "YYYY-MM-DD" (opcional)
    }
    
    Returns:
        200: {"ok": true, "message": "...", "id": int}
        400: {"ok": false, "message": "Error"}
    """
    try:
        data = request.get_json() or {}
        
        result = attendance_service.mark_attendance(
            student_id=data.get('student_id'),
            course_id=data.get('course_id'),
            status=data.get('status', 'presente'),
            entry_time=data.get('entry_time'),
            exit_time=data.get('exit_time'),
            attendance_date=data.get('attendance_date')
        )
        
        status_code = 200 if result.get('ok') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al marcar asistencia: {str(e)}"
        }), 500


@attendance_bp.get('/student/<int:student_id>')
@jwt_required()
def get_student_attendance(student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene el registro de asistencia de un estudiante.
    
    Query params:
        course_id: int (opcional) - Filtrar por curso
        start_date: YYYY-MM-DD (opcional)
        end_date: YYYY-MM-DD (opcional)
        limit: int (default 50)
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
        404: {"ok": false, "message": "Estudiante no encontrado"}
    """
    try:
        course_id = request.args.get('course_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 50, type=int)
        
        result = attendance_service.get_student_attendance(
            student_id=student_id,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener asistencia: {str(e)}"
        }), 500


@attendance_bp.get('/course/<int:course_id>')
@jwt_required()
def get_course_attendance(course_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene la asistencia de todos los estudiantes en un curso.
    
    Query params:
        date: YYYY-MM-DD (opcional) - Filtrar por fecha
        status: presente|tardanza|falta|salida_repentina (opcional)
        limit: int (default 100)
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
    """
    try:
        attendance_date = request.args.get('date')
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        
        result = attendance_service.get_course_attendance(
            course_id=course_id,
            attendance_date=attendance_date,
            status=status,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener asistencia del curso: {str(e)}"
        }), 500


@attendance_bp.get('/stats/student/<int:student_id>')
@jwt_required()
def get_attendance_stats(student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene estadísticas de asistencia de un estudiante.
    
    Query params:
        course_id: int (opcional)
    
    Returns:
        200: {
            "ok": true,
            "data": {
                "total_sessions": int,
                "present": int,
                "late": int,
                "absent": int,
                "early_exit": int,
                "attendance_rate": float
            }
        }
    """
    try:
        course_id = request.args.get('course_id', type=int)
        
        result = attendance_service.get_attendance_stats(
            student_id=student_id,
            course_id=course_id
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener estadísticas: {str(e)}"
        }), 500


@attendance_bp.get('/alerts/student/<int:student_id>')
@jwt_required()
def get_absence_alerts(student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene alertas de inasistencia para un estudiante.
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
        404: {"ok": false, "message": "Estudiante no encontrado"}
    """
    try:
        result = attendance_service.get_absence_alerts(student_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener alertas: {str(e)}"
        }), 500


@attendance_bp.put('/update/<int:attendance_id>')
@jwt_required()
def update_attendance(attendance_id: int) -> tuple[Dict[str, Any], int]:
    """
    Actualiza un registro de asistencia.
    
    Body JSON:
    {
        "status": "presente|tardanza|falta|salida_repentina",
        "entry_time": "HH:MM:SS" (opcional),
        "exit_time": "HH:MM:SS" (opcional)
    }
    
    Returns:
        200: {"ok": true, "message": "Actualizado"}
        404: {"ok": false, "message": "Registro no encontrado"}
    """
    try:
        data = request.get_json() or {}
        
        result = attendance_service.update_attendance(
            attendance_id=attendance_id,
            status=data.get('status'),
            entry_time=data.get('entry_time'),
            exit_time=data.get('exit_time')
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al actualizar asistencia: {str(e)}"
        }), 500


@attendance_bp.delete('/delete/<int:attendance_id>')
@jwt_required()
def delete_attendance(attendance_id: int) -> tuple[Dict[str, Any], int]:
    """
    Elimina un registro de asistencia.
    
    Returns:
        200: {"ok": true, "message": "Eliminado"}
        404: {"ok": false, "message": "Registro no encontrado"}
    """
    try:
        result = attendance_service.delete_attendance(attendance_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al eliminar asistencia: {str(e)}"
        }), 500
