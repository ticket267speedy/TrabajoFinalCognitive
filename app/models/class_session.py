from app.extensions import db
from sqlalchemy.sql import func


class ClassSession(db.Model):
    __tablename__ = 'class_sessions'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    end_time = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(
        db.Enum('active', 'finished', name='session_status_enum'),
        nullable=False,
        default='active'
    )

    course = db.relationship('Course')