#!/usr/bin/env python3
"""Script para generar hashes de contraseña correctos"""

import os
import sys
from werkzeug.security import generate_password_hash

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User

def fix_passwords():
    """Actualiza las contraseñas con hashes correctos"""
    app = create_app()
    
    with app.app_context():
        try:
            users = User.query.all()
            
            for user in users:
                # Generar hash de la contraseña
                password_hash = generate_password_hash(user.password_text)
                user.password_hash = password_hash
                print(f"✅ Actualizado hash para {user.email}")
            
            db.session.commit()
            print("✅ Todas las contraseñas han sido actualizadas con hashes correctos")
            
            # Mostrar información de los usuarios
            print("\n📋 Usuarios en la base de datos:")
            for user in users:
                print(f"   - {user.email} ({user.role}) - {user.first_name} {user.last_name}")
                if user.description:
                    print(f"     Descripción: {user.description[:50]}...")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar contraseñas: {e}")
            return False

if __name__ == "__main__":
    fix_passwords()