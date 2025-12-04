"""
Repositorio de Estudiantes

Contiene todas las operaciones CRUD para estudiantes.
"""
from typing import Tuple, List, Optional, Dict, Any
from app.extensions import db
from app.models import Student, Enrollment, Course


def get_all_students_repo(limit: int = 50, offset: int = 0, course_id: Optional[int] = None) -> Tuple[List[Student], int]:
    """Obtiene todos los estudiantes con paginación"""
    query = Student.query
    
    if course_id:
        query = query.join(Enrollment).filter(Enrollment.course_id == course_id).distinct()
    
    total = query.count()
    students = query.order_by(Student.created_at.desc()).limit(limit).offset(offset).all()
    
    return students, total


def get_student_by_id_repo(student_id: int) -> Optional[Student]:
    """Obtiene un estudiante por ID"""
    return Student.query.get(student_id)


def create_student_repo(name: str, email: str, id_number: str, phone: Optional[str] = None) -> Student:
    """Crea un nuevo estudiante"""
    student = Student(
        name=name,
        email=email,
        id_number=id_number,
        phone=phone
    )
    db.session.add(student)
    db.session.commit()
    return student


def update_student_repo(student_id: int, **kwargs) -> Optional[Student]:
    """Actualiza datos de un estudiante"""
    student = Student.query.get(student_id)
    
    if not student:
        return None
    
    for key, value in kwargs.items():
        if hasattr(student, key) and value is not None:
            setattr(student, key, value)
    
    db.session.commit()
    return student


def delete_student_repo(student_id: int) -> bool:
    """Elimina un estudiante"""
    student = Student.query.get(student_id)
    
    if not student:
        return False
    
    db.session.delete(student)
    db.session.commit()
    return True


def get_student_courses_repo(student_id: int) -> List[Dict[str, Any]]:
    """Obtiene los cursos en que está inscrito un estudiante"""
    courses = db.session.query(Course).join(
        Enrollment, Course.id == Enrollment.course_id
    ).filter(
        Enrollment.student_id == student_id
    ).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "description": c.description,
            "schedule": c.schedule
        }
        for c in courses
    ]
