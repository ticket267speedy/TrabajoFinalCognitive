"""
Autenticación y Autorización

Este módulo maneja toda la lógica de autenticación de usuarios,
incluyendo login, generación de tokens JWT, y validación de permisos.

Flujo de Autenticación:
1. El usuario envía email/contraseña al endpoint /login
2. El servidor valida las credenciales contra la BD
3. Si son válidas, genera un JWT con el rol del usuario
4. El cliente almacena el token (generalmente en localStorage)
5. En cada petición, el token se envía en el header "Authorization: Bearer <token>"
6. El servidor valida el token y extrae la identidad del usuario
7. Se verifica el rol del usuario para autorización

Roles disponibles:
- 'admin': Administrador del sistema (acceso total)
- 'advisor': Asesor de becas (gestión de becarios)
- 'client': Profesor/Usuario regular
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, Tuple

from flask import request, jsonify, current_app
from app.models import User


# Configuración de tokens JWT
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def generate_token(user_id: int, user_role: str) -> str:
    """
    Genera un token JWT para un usuario.
    
    El token contiene:
    - user_id: ID del usuario en la BD
    - role: Rol del usuario (admin, advisor, client)
    - exp: Timestamp de expiración (24 horas por defecto)
    - iat: Timestamp de creación
    
    Args:
        user_id: ID del usuario autenticado
        user_role: Rol del usuario en el sistema
    
    Returns:
        String con el token JWT codificado
    
    Ejemplo:
        >>> token = generate_token(user_id=1, user_role='admin')
        >>> # Token se ve así: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    payload = {
        'user_id': user_id,
        'role': user_role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token JWT.
    
    Validaciones realizadas:
    - Comprueba que la firma sea válida (no haya sido modificado)
    - Comprueba que no haya expirado
    - Extrae los datos del usuario
    
    Args:
        token: String con el token JWT a verificar
    
    Returns:
        Dict con el payload del token si es válido, None si no lo es
    
    Ejemplo:
        >>> payload = verify_token('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
        >>> print(payload['user_id'])  # 1
        >>> print(payload['role'])      # 'admin'
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # El token expiró
        return None
    except jwt.InvalidTokenError:
        # El token es inválido o fue modificado
        return None


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Autentica un usuario con email y contraseña.
    
    Pasos:
    1. Busca el usuario en la BD por email
    2. Valida que la contraseña sea correcta
    3. Si es válido, genera un token JWT
    4. Retorna el token y los datos del usuario
    
    Args:
        email: Email del usuario
        password: Contraseña sin encriptar
    
    Returns:
        Tuple con:
        - success (bool): True si la autenticación fue exitosa
        - message (str): Mensaje de éxito o error
        - user_data (dict): Datos del usuario si fue exitoso, None en caso contrario
    
    Ejemplo:
        >>> success, msg, user = login_user('profesor@example.com', 'password123')
        >>> if success:
        ...     print(f"Token: {user['token']}")
        ...     print(f"Rol: {user['role']}")
    """
    try:
        # Buscar usuario por email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return False, "Usuario no encontrado", None
        
        # Verificar contraseña (aquí deberías usar hashing en producción)
        if user.password_text != password:
            return False, "Contraseña incorrecta", None
        
        # Generar token JWT
        token = generate_token(user.id, user.role)
        
        # Retornar datos del usuario con token
        user_data = {
            'token': token,
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'profile_photo_url': user.profile_photo_url
        }
        
        return True, "Autenticación exitosa", user_data
        
    except Exception as e:
        return False, f"Error de autenticación: {str(e)}", None


def token_required(f):
    """
    Decorador para proteger endpoints que requieren autenticación.
    
    Uso:
        @app.route('/api/protected')
        @token_required
        def protected_endpoint():
            # request.user contiene los datos del usuario autenticado
            return jsonify({'user_id': request.user['user_id']})
    
    El decorador:
    1. Extrae el token del header "Authorization"
    2. Lo verifica y decodifica
    3. Si es inválido, retorna error 401
    4. Si es válido, añade los datos a request.user
    
    Header esperado:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar el token en el header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # El formato es "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401
        
        # Verificar el token
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token inválido o expirado'}), 401
        
        # Guardar los datos del usuario en request para usarlos en la función
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated


def role_required(required_role: str):
    """
    Decorador para verificar que el usuario tiene un rol específico.
    
    Uso:
        @app.route('/api/admin')
        @token_required
        @role_required('admin')
        def admin_endpoint():
            return jsonify({'message': 'Solo para administradores'})
    
    Siempre se debe usar después de @token_required porque depende
    de que request.user exista.
    
    Args:
        required_role: El rol requerido ('admin', 'advisor', 'client')
    
    Roles y permisos:
    - 'admin': Puede hacer todo (crear usuarios, cursos, etc.)
    - 'advisor': Puede gestionar becarios y sus alertas
    - 'client': Puede ver sus propios datos y cursos
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'message': 'Usuario no autenticado'}), 401
            
            if request.user['role'] != required_role:
                return jsonify({
                    'message': f'Se requiere rol "{required_role}", pero tienes "{request.user["role"]}"'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def get_current_user() -> Optional[User]:
    """
    Obtiene el usuario actualmente autenticado.
    
    Usa los datos almacenados en request.user por el decorador
    @token_required.
    
    Returns:
        Objeto User si está autenticado, None en caso contrario
    
    Ejemplo:
        @app.route('/api/me')
        @token_required
        def get_my_profile():
            user = get_current_user()
            return jsonify(user.to_dict())
    """
    if not hasattr(request, 'user'):
        return None
    
    user_id = request.user.get('user_id')
    if user_id:
        return User.query.get(user_id)
    
    return None


def check_permission(user: User, resource_owner_id: int, allow_admin: bool = True) -> bool:
    """
    Verifica si un usuario tiene permiso para acceder a un recurso.
    
    Reglas:
    - admin: Siempre tiene acceso a todo (si allow_admin=True)
    - Otros usuarios: Solo pueden acceder a sus propios recursos
    
    Args:
        user: Objeto User autenticado
        resource_owner_id: ID del propietario del recurso
        allow_admin: Si es True, los administradores tienen acceso a todo
    
    Returns:
        True si tiene permiso, False en caso contrario
    
    Ejemplo:
        @app.route('/api/students/<int:student_id>')
        @token_required
        def get_student(student_id):
            user = get_current_user()
            if not check_permission(user, student_id):
                return jsonify({'message': 'Permiso denegado'}), 403
            # ... obtener estudiante
    """
    if allow_admin and user.role == 'admin':
        return True
    
    return user.id == resource_owner_id
