"""
Controlador de Cursos

Gestiona rutas para:
- Listar cursos
- Crear/editar/eliminar cursos
- Inscribir/desincribir estudiantes
- Obtener estudiantes de un curso
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from typing import Dict, Any

from ...services.course_service import CourseService

# Blueprint
courses_bp = Blueprint(
    'courses',
    __name__,
    url_prefix='/api/courses'
)

course_service = CourseService()


@courses_bp.get('/')
@jwt_required()
def list_courses() -> tuple[Dict[str, Any], int]:
    """
    Obtiene lista de cursos.
    
    Query params:
        limit: int (default 50)
        offset: int (default 0)
        status: active|inactive (opcional)
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status')
        
        result = course_service.get_all_courses(
            limit=limit,
            offset=offset,
            status=status
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener cursos: {str(e)}"
        }), 500


@courses_bp.get('/<int:course_id>')
@jwt_required()
def get_course_detail(course_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene detalles de un curso.
    
    Returns:
        200: {"ok": true, "data": {...}}
        404: {"ok": false, "message": "Curso no encontrado"}
    """
    try:
        result = course_service.get_course_by_id(course_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener curso: {str(e)}"
        }), 500


@courses_bp.post('/')
@jwt_required()
def create_course() -> tuple[Dict[str, Any], int]:
    """
    Crea un nuevo curso.
    
    Body JSON:
    {
        "name": str,
        "code": str,
        "description": str (opcional),
        "instructor_id": int,
        "schedule": str (opcional)
    }
    
    Returns:
        201: {"ok": true, "id": int, "message": "Curso creado"}
        400: {"ok": false, "message": "Error"}
    """
    try:
        data = request.get_json() or {}
        
        result = course_service.create_course(
            name=data.get('name'),
            code=data.get('code'),
            description=data.get('description'),
            instructor_id=data.get('instructor_id'),
            schedule=data.get('schedule')
        )
        
        status_code = 201 if result.get('ok') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al crear curso: {str(e)}"
        }), 500


@courses_bp.put('/<int:course_id>')
@jwt_required()
def update_course(course_id: int) -> tuple[Dict[str, Any], int]:
    """
    Actualiza datos de un curso.
    
    Body JSON:
    {
        "name": str (opcional),
        "description": str (opcional),
        "schedule": str (opcional),
        "status": str (opcional)
    }
    
    Returns:
        200: {"ok": true, "message": "Actualizado"}
        404: {"ok": false, "message": "Curso no encontrado"}
    """
    try:
        data = request.get_json() or {}
        
        result = course_service.update_course(
            course_id=course_id,
            **{k: v for k, v in data.items() if v is not None}
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al actualizar curso: {str(e)}"
        }), 500


@courses_bp.delete('/<int:course_id>')
@jwt_required()
def delete_course(course_id: int) -> tuple[Dict[str, Any], int]:
    """
    Elimina un curso.
    
    Returns:
        200: {"ok": true, "message": "Eliminado"}
        404: {"ok": false, "message": "Curso no encontrado"}
    """
    try:
        result = course_service.delete_course(course_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al eliminar curso: {str(e)}"
        }), 500


@courses_bp.post('/<int:course_id>/enroll')
@jwt_required()
def enroll_student(course_id: int) -> tuple[Dict[str, Any], int]:
    """
    Inscribe un estudiante en un curso.
    
    Body JSON:
    {
        "student_id": int
    }
    
    Returns:
        200: {"ok": true, "message": "Inscrito"}
        400: {"ok": false, "message": "Error"}
    """
    try:
        data = request.get_json() or {}
        
        result = course_service.enroll_student(
            course_id=course_id,
            student_id=data.get('student_id')
        )
        
        status_code = 200 if result.get('ok') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al inscribir estudiante: {str(e)}"
        }), 500


@courses_bp.delete('/<int:course_id>/unenroll/<int:student_id>')
@jwt_required()
def unenroll_student(course_id: int, student_id: int) -> tuple[Dict[str, Any], int]:
    """
    Desincribe un estudiante de un curso.
    
    Returns:
        200: {"ok": true, "message": "Desincrito"}
        404: {"ok": false, "message": "Enrollment no encontrado"}
    """
    try:
        result = course_service.unenroll_student(
            course_id=course_id,
            student_id=student_id
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al desincribir estudiante: {str(e)}"
        }), 500


@courses_bp.get('/<int:course_id>/students')
@jwt_required()
def get_course_students(course_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene los estudiantes inscritos en un curso.
    
    Query params:
        limit: int (default 100)
        offset: int (default 0)
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
        404: {"ok": false, "message": "Curso no encontrado"}
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = course_service.get_course_students(
            course_id=course_id,
            limit=limit,
            offset=offset
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener estudiantes del curso: {str(e)}"
        }), 500
