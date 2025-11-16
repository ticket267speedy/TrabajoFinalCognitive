from app.extensions import db


class CourseSchedule(db.Model):
    __tablename__ = 'course_schedule'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Domingo..6=Sábado
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    course = db.relationship('Course')

    __table_args__ = (
        db.Index('idx_schedule_course', 'course_id'),
    )

    def __repr__(self):
        return f'<CourseSchedule course={self.course_id} day={self.day_of_week}>'