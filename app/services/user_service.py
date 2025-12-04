"""
Servicio de Usuarios

Orquesta la lógica de negocio para operaciones con usuarios.
Utiliza el repositorio para acceder a datos.
"""
from typing import Dict, Any, Optional
from ..repositories.users.users_repository import (
    get_all_users_repo,
    get_user_by_id_repo,
    get_user_by_email_repo,
    create_user_repo,
    update_user_repo,
    delete_user_repo,
    change_password_repo
)
from ..models import User


class UserService:
    """Servicio para gestionar usuarios"""
    
    def get_all_users(self, limit: int = 50, offset: int = 0, role: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene todos los usuarios con paginación"""
        try:
            users, total = get_all_users_repo(limit=limit, offset=offset, role=role)
            
            return {
                "ok": True,
                "data": [self._user_to_dict(u) for u in users],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener usuarios: {str(e)}"
            }
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Obtiene un usuario por ID"""
        try:
            user = get_user_by_id_repo(user_id)
            
            if not user:
                return {
                    "ok": False,
                    "message": f"Usuario {user_id} no encontrado"
                }
            
            return {
                "ok": True,
                "data": self._user_to_dict(user)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener usuario: {str(e)}"
            }
    
    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Obtiene un usuario por email"""
        try:
            user = get_user_by_email_repo(email)
            
            if not user:
                return {
                    "ok": False,
                    "message": f"Usuario con email {email} no encontrado"
                }
            
            return {
                "ok": True,
                "data": self._user_to_dict(user)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener usuario: {str(e)}"
            }
    
    def create_user(self, email: str, password: str, full_name: str, role: str = "student", 
                   is_active: bool = True) -> Dict[str, Any]:
        """Crea un nuevo usuario"""
        try:
            if not email or not password or not full_name:
                return {
                    "ok": False,
                    "message": "email, password y full_name son requeridos"
                }
            
            # Validar role
            valid_roles = ['admin', 'advisor', 'student']
            if role not in valid_roles:
                return {
                    "ok": False,
                    "message": f"role debe ser uno de: {', '.join(valid_roles)}"
                }
            
            # Verificar que el email no exista
            existing = get_user_by_email_repo(email)
            if existing:
                return {
                    "ok": False,
                    "message": f"El email {email} ya está registrado"
                }
            
            user = create_user_repo(
                email=email,
                password=password,
                full_name=full_name,
                role=role,
                is_active=is_active
            )
            
            return {
                "ok": True,
                "id": user.id,
                "message": "Usuario creado exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al crear usuario: {str(e)}"
            }
    
    def update_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Actualiza datos de un usuario"""
        try:
            user = update_user_repo(user_id, **kwargs)
            
            if not user:
                return {
                    "ok": False,
                    "message": f"Usuario {user_id} no encontrado"
                }
            
            return {
                "ok": True,
                "message": "Usuario actualizado exitosamente",
                "data": self._user_to_dict(user)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al actualizar usuario: {str(e)}"
            }
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Elimina un usuario"""
        try:
            success = delete_user_repo(user_id)
            
            if not success:
                return {
                    "ok": False,
                    "message": f"Usuario {user_id} no encontrado"
                }
            
            return {
                "ok": True,
                "message": "Usuario eliminado exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al eliminar usuario: {str(e)}"
            }
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """Cambia la contraseña de un usuario"""
        try:
            if not old_password or not new_password:
                return {
                    "ok": False,
                    "message": "old_password y new_password son requeridos"
                }
            
            user = get_user_by_id_repo(user_id)
            if not user:
                return {
                    "ok": False,
                    "message": f"Usuario {user_id} no encontrado"
                }
            
            # Verificar contraseña antigua
            if not user.check_password(old_password):
                return {
                    "ok": False,
                    "message": "Contraseña actual incorrecta"
                }
            
            # Cambiar contraseña
            success = change_password_repo(user_id, new_password)
            
            if not success:
                return {
                    "ok": False,
                    "message": "Error al cambiar contraseña"
                }
            
            return {
                "ok": True,
                "message": "Contraseña actualizada exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al cambiar contraseña: {str(e)}"
            }
    
    @staticmethod
    def _user_to_dict(user: User) -> Dict[str, Any]:
        """Convierte un objeto User a diccionario (sin password)"""
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
