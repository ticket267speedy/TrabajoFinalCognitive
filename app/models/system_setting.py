from app.extensions import db


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_format = db.Column(db.String(20), nullable=False, default='DD/MM/YYYY')
    time_format = db.Column(db.String(10), nullable=False, default='24h')
    interface_animations = db.Column(db.Boolean, nullable=False, default=True)
    tardiness_tolerance_minutes = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

    user = db.relationship('User')

    __table_args__ = (
        db.UniqueConstraint('user_id', name='uq_system_setting_user'),
    )

    def __repr__(self):
        return f'<SystemSetting user={self.user_id}>'