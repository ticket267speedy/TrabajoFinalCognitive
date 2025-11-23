
from app.extensions import db
from sqlalchemy.sql import func

class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Alert {self.id} for Student {self.student_id}>'