from app.extensions import db
from datetime import datetime


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    student = db.relationship('Student')
    course = db.relationship('Course')

    def __repr__(self):
        return f'<Enrollment {self.student_id} - {self.course_id}>'