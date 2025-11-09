from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Almacenamos la contraseña (ahora puede ser hash largo)
    password_text = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)

    # Perfil
    profile_photo_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    # El rol define tipo de usuario en la plataforma
    role = db.Column(
        db.Enum('admin', 'client', 'advisor', name='user_roles_enum'),
        nullable=False,
        default='client'
    )

    def __repr__(self):
        return f'<User {self.email}>'