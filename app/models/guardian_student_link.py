from app.extensions import db
from sqlalchemy.sql import func


class GuardianStudentLink(db.Model):
    __tablename__ = 'guardian_student_links'

    id = db.Column(db.Integer, primary_key=True)
    guardian_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    relationship = db.Column(db.String(50), nullable=True)  # e.g., 'parent', 'tutor'
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    guardian = db.relationship('User')
    student = db.relationship('Student')

    def __repr__(self):
        return f'<GuardianStudentLink guardian={self.guardian_user_id} student={self.student_id}>'