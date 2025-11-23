from app.extensions import db
from datetime import datetime, date


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    entry_time = db.Column(db.Time, nullable=True)  # Hora real de entrada
    exit_time = db.Column(db.Time, nullable=True)   # Hora real de salida
    status = db.Column(
        db.Enum('presente', 'tardanza', 'falta', 'salida_repentina', name='attendance_status_enum'),
        nullable=False,
        default='falta'
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    student = db.relationship('Student')
    course = db.relationship('Course')

    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.course_id} - {self.date} - {self.status}>'
