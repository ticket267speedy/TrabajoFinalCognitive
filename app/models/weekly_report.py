from app.extensions import db


class WeeklyReport(db.Model):
    __tablename__ = 'weekly_reports'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    week_end_date = db.Column(db.Date, nullable=False)
    total_students = db.Column(db.Integer, nullable=True)
    total_present = db.Column(db.Integer, nullable=True)
    total_absent = db.Column(db.Integer, nullable=True)
    attendance_percentage = db.Column(db.Float, nullable=True)
    report_data = db.Column(db.Text, nullable=True)  # JSON con datos detallados
    generated_at = db.Column(db.DateTime(timezone=True))

    course = db.relationship('Course')

    __table_args__ = (
        db.Index('idx_weekly_course_date', 'course_id', 'week_start_date'),
    )

    def __repr__(self):
        return f'<WeeklyReport course={self.course_id} week={self.week_start_date}>'