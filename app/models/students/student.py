"""Modelos de Estudiantes"""
from app.extensions import db
from datetime import datetime


class Student(db.Model):
    """
    Modelo de Estudiante.
    
    Representa a un estudiante en el sistema. Puede estar vinculado a
    múltiples cursos (enrollments) y tener registros de asistencia.
    """
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_scholarship_student = db.Column(db.Boolean, nullable=False, default=False)
    profile_photo_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relaciones con otros modelos
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='student', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student {self.id} - {self.first_name} {self.last_name}>'
