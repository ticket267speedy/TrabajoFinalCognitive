"""
Controlador de Usuarios

Gestiona rutas para:
- Listar usuarios
- Crear/editar/eliminar usuarios
- Cambiar contraseña
- Actualizar perfil
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any

from ...services.user_service import UserService

# Blueprint
users_bp = Blueprint(
    'users',
    __name__,
    url_prefix='/api/users'
)

user_service = UserService()


@users_bp.get('/')
@jwt_required()
def list_users() -> tuple[Dict[str, Any], int]:
    """
    Obtiene lista de usuarios.
    
    Query params:
        limit: int (default 50)
        offset: int (default 0)
        role: admin|advisor|student (opcional)
    
    Returns:
        200: {"ok": true, "data": [...], "total": int}
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        role = request.args.get('role')
        
        result = user_service.get_all_users(
            limit=limit,
            offset=offset,
            role=role
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener usuarios: {str(e)}"
        }), 500


@users_bp.get('/profile')
@jwt_required()
def get_current_user_profile() -> tuple[Dict[str, Any], int]:
    """
    Obtiene el perfil del usuario actual (autenticado).
    
    Returns:
        200: {"ok": true, "data": {...}}
        404: {"ok": false, "message": "Usuario no encontrado"}
    """
    try:
        user_id = get_jwt_identity()
        
        result = user_service.get_user_by_id(user_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener perfil: {str(e)}"
        }), 500


@users_bp.get('/<int:user_id>')
@jwt_required()
def get_user_detail(user_id: int) -> tuple[Dict[str, Any], int]:
    """
    Obtiene detalles de un usuario específico.
    
    Returns:
        200: {"ok": true, "data": {...}}
        404: {"ok": false, "message": "Usuario no encontrado"}
    """
    try:
        result = user_service.get_user_by_id(user_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al obtener usuario: {str(e)}"
        }), 500


@users_bp.post('/')
@jwt_required()
def create_user() -> tuple[Dict[str, Any], int]:
    """
    Crea un nuevo usuario.
    
    Body JSON:
    {
        "email": str,
        "password": str,
        "full_name": str,
        "role": "admin|advisor|student",
        "is_active": bool (opcional, default true)
    }
    
    Returns:
        201: {"ok": true, "id": int, "message": "Usuario creado"}
        400: {"ok": false, "message": "Error"}
    """
    try:
        data = request.get_json() or {}
        
        result = user_service.create_user(
            email=data.get('email'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            role=data.get('role'),
            is_active=data.get('is_active', True)
        )
        
        status_code = 201 if result.get('ok') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al crear usuario: {str(e)}"
        }), 500


@users_bp.put('/profile')
@jwt_required()
def update_current_user_profile() -> tuple[Dict[str, Any], int]:
    """
    Actualiza el perfil del usuario actual.
    
    Body JSON:
    {
        "full_name": str (opcional),
        "phone": str (opcional),
        "bio": str (opcional)
    }
    
    Returns:
        200: {"ok": true, "message": "Perfil actualizado"}
        404: {"ok": false, "message": "Usuario no encontrado"}
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        result = user_service.update_user(
            user_id=user_id,
            **{k: v for k, v in data.items() if v is not None}
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al actualizar perfil: {str(e)}"
        }), 500


@users_bp.put('/<int:user_id>')
@jwt_required()
def update_user(user_id: int) -> tuple[Dict[str, Any], int]:
    """
    Actualiza datos de un usuario (Admin only).
    
    Body JSON:
    {
        "full_name": str (opcional),
        "email": str (opcional),
        "role": str (opcional),
        "is_active": bool (opcional)
    }
    
    Returns:
        200: {"ok": true, "message": "Actualizado"}
        404: {"ok": false, "message": "Usuario no encontrado"}
    """
    try:
        data = request.get_json() or {}
        
        result = user_service.update_user(
            user_id=user_id,
            **{k: v for k, v in data.items() if v is not None}
        )
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al actualizar usuario: {str(e)}"
        }), 500


@users_bp.post('/change-password')
@jwt_required()
def change_password() -> tuple[Dict[str, Any], int]:
    """
    Cambia la contraseña del usuario actual.
    
    Body JSON:
    {
        "old_password": str,
        "new_password": str
    }
    
    Returns:
        200: {"ok": true, "message": "Contraseña actualizada"}
        400: {"ok": false, "message": "Error"}
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        result = user_service.change_password(
            user_id=user_id,
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        
        status_code = 200 if result.get('ok') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al cambiar contraseña: {str(e)}"
        }), 500


@users_bp.delete('/<int:user_id>')
@jwt_required()
def delete_user(user_id: int) -> tuple[Dict[str, Any], int]:
    """
    Elimina un usuario (Admin only).
    
    Returns:
        200: {"ok": true, "message": "Eliminado"}
        404: {"ok": false, "message": "Usuario no encontrado"}
    """
    try:
        result = user_service.delete_user(user_id)
        
        if not result.get('ok'):
            return jsonify(result), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al eliminar usuario: {str(e)}"
        }), 500
