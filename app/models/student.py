from app.extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)

    # Bandera para perfil Cliente (PRONABEC) - alumnos becados
    is_scholarship_student = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Student {self.id}>'