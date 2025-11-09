from app.extensions import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    admin = db.relationship('User')