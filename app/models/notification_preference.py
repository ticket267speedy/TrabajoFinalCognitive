from app.extensions import db


class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email_notifications = db.Column(db.Boolean, nullable=False, default=True)
    student_alerts = db.Column(db.Boolean, nullable=False, default=True)
    weekly_summary = db.Column(db.Boolean, nullable=False, default=True)
    absence_threshold = db.Column(db.Integer, nullable=False, default=3)
    summary_day = db.Column(db.String(20), nullable=False, default='Friday')
    summary_time = db.Column(db.Time, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

    user = db.relationship('User')

    __table_args__ = (
        db.UniqueConstraint('user_id', name='uq_notification_pref_user'),
    )

    def __repr__(self):
        return f'<NotificationPreference user={self.user_id}>'