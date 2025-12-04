"""Modelos de Asistencia"""
from app.extensions import db
from datetime import datetime, date
from sqlalchemy.sql import func


class Attendance(db.Model):
    """
    Modelo de Asistencia.
    
    Registra la asistencia de un estudiante en un curso.
    Estados posibles:
    - 'presente': Llegó a tiempo
    - 'tardanza': Llegó tarde
    - 'falta': No asistió
    - 'salida_repentina': Se fue sin justificación
    """
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    entry_time = db.Column(db.Time, nullable=True)
    exit_time = db.Column(db.Time, nullable=True)
    status = db.Column(
        db.Enum('presente', 'tardanza', 'falta', 'salida_repentina', name='attendance_status_enum'),
        nullable=False,
        default='falta'
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.course_id} - {self.date} - {self.status}>'


class Alert(db.Model):
    """
    Modelo de Alerta.
    
    Genera alertas para estudiantes cuando tiene muchas faltas
    o se dispara automáticamente por bajo rendimiento.
    """
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Alert {self.id} for Student {self.student_id}>'
