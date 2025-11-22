from app.extensions import db
from sqlalchemy import text


class ClassSession(db.Model):
    __tablename__ = 'class_sessions'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    # PostgreSQL timestamp with timezone support
    start_time = db.Column(db.DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    end_time = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(
        db.Enum('active', 'finished', name='session_status_enum'),
        nullable=False,
        default='active'
    )

    course = db.relationship('Course')