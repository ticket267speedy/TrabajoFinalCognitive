from app.extensions import db


class AttendanceSummary(db.Model):
    __tablename__ = 'attendance_summaries'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('class_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    presence_percentage = db.Column(db.Float, nullable=False, default=0.0)
    is_manual_override = db.Column(db.Boolean, nullable=False, default=False)

    session = db.relationship('ClassSession')
    student = db.relationship('Student')