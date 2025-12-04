"""
Controlador de Estudiantes

Gestiona rutas para:
- Obtener lista de estudiantes
- Crear/editar/eliminar estudiantes
- Obtener perfil de estudiante
- Listar enrollments de un estudiante
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from typing import Dict, Any

from ...services.student_service import StudentService

# Blueprint
students_bp = Blueprint(
    'students',
    __name__,
    url_prefix='/api/students'
)

student_service = StudentService()


@students_bp.get('/')
@jwt_required()
def list_students() -> tuple[Dict[str, Any], int]:
    """
    Obtiene lista de estudiantes.
    
    Query params:
        limit: int (default 50)
        offset: int (default 0)
        course_id: int (opcional) - Filtrar por curso
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        course_id = request.args.get('course_id', type=int)
        
        result = student_service.get_all_students(
            limit=limit,
            offset=offset,
            course_id=course_id
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener estudiantes: {str(e)}"
        }), 500


@students_bp.get('/<int:student_id>')
@jwt_required()
def get_student_detail(student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene detalles de un estudiante específico.
    
    Returns:
        200: {"ok": true, "data": {...}}
        404: {"ok": false, "message": "Estudiante no encontrado"}
    """
    try:
        result = student_service.get_student_by_id(student_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener estudiante: {str(e)}"
        }), 500


@students_bp.post('/')
@jwt_required()
def create_student() -> tuple[Dict[str, Any], int]:
    """
    Crea un nuevo estudiante.
    
    Body JSON:
    {
        "name": str,
        "email": str,
        "id_number": str,
        "phone": str (opcional)
    }
    
    Returns:
        201: {"ok": true, "id": int, "message": "Estudiante creado"}
        400: {"ok": false, "message": "Error"}
    """
    try:
        data = request.get_json() or {}
        
        result = student_service.create_student(
            name=data.get('name'),
            email=data.get('email'),
            id_number=data.get('id_number'),
            phone=data.get('phone')
        )
        
        status_code = 201 if result.get('ok') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al crear estudiante: {str(e)}"
        }), 500


@students_bp.put('/<int:student_id>')
@jwt_required()
def update_student(student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Actualiza datos de un estudiante.
    
    Body JSON:
    {
        "name": str (opcional),
        "email": str (opcional),
        "phone": str (opcional)
    }
    
    Returns:
        200: {"ok": true, "message": "Actualizado"}
        404: {"ok": false, "message": "Estudiante no encontrado"}
    """
    try:
        data = request.get_json() or {}
        
        result = student_service.update_student(
            student_id=student_id,
            **{k: v for k, v in data.items() if v is not None}
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al actualizar estudiante: {str(e)}"
        }), 500


@students_bp.delete('/<int:student_id>')
@jwt_required()
def delete_student(student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Elimina un estudiante.
    
    Returns:
        200: {"ok": true, "message": "Eliminado"}
        404: {"ok": false, "message": "Estudiante no encontrado"}
    """
    try:
        result = student_service.delete_student(student_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al eliminar estudiante: {str(e)}"
        }), 500


@students_bp.get('/<int:student_id>/courses')
@jwt_required()
def get_student_courses(student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene los cursos en que está inscrito un estudiante.
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
        404: {"ok": false, "message": "Estudiante no encontrado"}
    """
    try:
        result = student_service.get_student_courses(student_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener cursos del estudiante: {str(e)}"
        }), 500
