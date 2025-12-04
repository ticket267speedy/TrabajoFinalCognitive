"""Modelos de Cursos"""
from app.extensions import db
from datetime import datetime


class Course(db.Model):
    """
    Modelo de Curso.
    
    Representa un curso dictado por un profesor (admin).
    Puede tener múltiples estudiantes enrollados (enrollments)
    y registros de asistencia.
    """
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    days_of_week = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relaciones
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='course', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='course', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "professor_name": f"{self.admin.first_name} {self.admin.last_name}" if self.admin else "Sin profesor",
            "students_count": len(self.enrollments),
        }


class Enrollment(db.Model):
    """
    Modelo de Matricula.
    
    Vincula a un estudiante con un curso.
    Representa que el estudiante está matriculado en ese curso.
    """
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Enrollment {self.student_id} - {self.course_id}>'
