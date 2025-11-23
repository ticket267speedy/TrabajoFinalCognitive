from app.extensions import db
from datetime import datetime


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=True)  # Ej: 08:00:00
    end_time = db.Column(db.Time, nullable=True)    # Ej: 10:00:00
    days_of_week = db.Column(db.String(100), nullable=True)  # Ej: "Lunes,Jueves"
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    admin = db.relationship('User')

    def __repr__(self):
        return f'<Course {self.name}>'