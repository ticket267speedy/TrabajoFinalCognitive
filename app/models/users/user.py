"""Modelos de Usuario"""
from app.extensions import db
from datetime import datetime


class User(db.Model):
    """
    Modelo de Usuario del Sistema.
    
    Representa a administradores, asesores y profesores en CogniPass.
    Roles disponibles:
    - 'admin': Administrador del sistema
    - 'advisor': Asesor de becas
    - 'professor': Profesor (puede dictar cursos)
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_text = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    profile_photo_url = db.Column(db.String(255), nullable=True)
    role = db.Column(
        db.Enum('admin', 'client', 'advisor', name='user_roles_enum'),
        nullable=False,
        default='client'
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Un usuario puede dictar muchos cursos
    courses = db.relationship('Course', backref='admin', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'
