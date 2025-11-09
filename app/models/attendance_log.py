from app.extensions import db
from sqlalchemy.sql import func


class AttendanceLog(db.Model):
    __tablename__ = 'attendance_logs'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('class_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    session = db.relationship('ClassSession')
    student = db.relationship('Student')