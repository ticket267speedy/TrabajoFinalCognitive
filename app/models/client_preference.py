from app.extensions import db


class ClientPreference(db.Model):
    __tablename__ = 'client_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notifications_enabled = db.Column(db.Boolean, nullable=False, default=True)
    allow_data_sharing = db.Column(db.Boolean, nullable=False, default=False)
    theme = db.Column(db.Enum('light', 'dark', name='client_theme_enum'), nullable=False, default='light')

    user = db.relationship('User')

    def __repr__(self):
        return f'<ClientPreference user={self.user_id}>'