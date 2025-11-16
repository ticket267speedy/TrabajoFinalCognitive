from app.extensions import db


class AttendanceAlertsConfig(db.Model):
    __tablename__ = 'attendance_alerts_config'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    alert_type = db.Column(
        db.Enum('consecutive_absence', 'low_percentage', 'late_pattern', name='attendance_alert_type_enum'),
        nullable=False
    )
    threshold_value = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    notification_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True))

    course = db.relationship('Course')

    def __repr__(self):
        return f'<AttendanceAlertsConfig course={self.course_id} type={self.alert_type}>'