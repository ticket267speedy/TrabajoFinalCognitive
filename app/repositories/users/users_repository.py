"""
Repositorio de Usuarios

Contiene todas las operaciones CRUD para usuarios.
"""
from typing import Tuple, List, Optional
from app.extensions import db
from app.models import User


def get_all_users_repo(limit: int = 50, offset: int = 0, role: Optional[str] = None) -> Tuple[List[User], int]:
    """Obtiene todos los usuarios con paginación"""
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()
    
    return users, total


def get_user_by_id_repo(user_id: int) -> Optional[User]:
    """Obtiene un usuario por ID"""
    return User.query.get(user_id)


def get_user_by_email_repo(email: str) -> Optional[User]:
    """Obtiene un usuario por email"""
    return User.query.filter_by(email=email).first()


def create_user_repo(email: str, password: str, full_name: str, role: str = "student",
                    is_active: bool = True) -> User:
    """Crea un nuevo usuario"""
    user = User(
        email=email,
        full_name=full_name,
        role=role,
        is_active=is_active
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def update_user_repo(user_id: int, **kwargs) -> Optional[User]:
    """Actualiza datos de un usuario"""
    user = User.query.get(user_id)
    
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key) and value is not None and key != 'password':
            setattr(user, key, value)
    
    db.session.commit()
    return user


def delete_user_repo(user_id: int) -> bool:
    """Elimina un usuario"""
    user = User.query.get(user_id)
    
    if not user:
        return False
    
    db.session.delete(user)
    db.session.commit()
    return True


def change_password_repo(user_id: int, new_password: str) -> bool:
    """Cambia la contraseña de un usuario"""
    user = User.query.get(user_id)
    
    if not user:
        return False
    
    user.set_password(new_password)
    db.session.commit()
    return True
