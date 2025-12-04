"""
Repositorio de Cursos

Contiene todas las operaciones CRUD para cursos.
"""
from typing import Tuple, List, Optional, Dict, Any
from app.extensions import db
from app.models import Course, Enrollment, Student


def get_all_courses_repo(limit: int = 50, offset: int = 0, status: Optional[str] = None) -> Tuple[List[Course], int]:
    """Obtiene todos los cursos con paginación"""
    query = Course.query
    
    if status:
        query = query.filter_by(status=status)
    
    total = query.count()
    courses = query.order_by(Course.created_at.desc()).limit(limit).offset(offset).all()
    
    return courses, total


def get_course_by_id_repo(course_id: int) -> Optional[Course]:
    """Obtiene un curso por ID"""
    return Course.query.get(course_id)


def create_course_repo(name: str, code: str, description: Optional[str] = None,
                      instructor_id: Optional[int] = None, schedule: Optional[str] = None) -> Course:
    """Crea un nuevo curso"""
    course = Course(
        name=name,
        code=code,
        description=description,
        instructor_id=instructor_id,
        schedule=schedule
    )
    db.session.add(course)
    db.session.commit()
    return course


def update_course_repo(course_id: int, **kwargs) -> Optional[Course]:
    """Actualiza datos de un curso"""
    course = Course.query.get(course_id)
    
    if not course:
        return None
    
    for key, value in kwargs.items():
        if hasattr(course, key) and value is not None:
            setattr(course, key, value)
    
    db.session.commit()
    return course


def delete_course_repo(course_id: int) -> bool:
    """Elimina un curso"""
    course = Course.query.get(course_id)
    
    if not course:
        return False
    
    db.session.delete(course)
    db.session.commit()
    return True


def enroll_student_repo(course_id: int, student_id: int) -> Optional[Enrollment]:
    """Inscribe un estudiante en un curso"""
    # Verificar que no esté ya inscrito
    existing = Enrollment.query.filter_by(
        course_id=course_id,
        student_id=student_id
    ).first()
    
    if existing:
        return None
    
    enrollment = Enrollment(
        course_id=course_id,
        student_id=student_id
    )
    db.session.add(enrollment)
    db.session.commit()
    return enrollment


def unenroll_student_repo(course_id: int, student_id: int) -> bool:
    """Desincribe un estudiante de un curso"""
    enrollment = Enrollment.query.filter_by(
        course_id=course_id,
        student_id=student_id
    ).first()
    
    if not enrollment:
        return False
    
    db.session.delete(enrollment)
    db.session.commit()
    return True


def get_course_students_repo(course_id: int, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """Obtiene los estudiantes inscritos en un curso"""
    query = db.session.query(Student).join(
        Enrollment, Student.id == Enrollment.student_id
    ).filter(
        Enrollment.course_id == course_id
    )
    
    total = query.count()
    students = query.order_by(Student.name).limit(limit).offset(offset).all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "id_number": s.id_number,
            "phone": s.phone
        }
        for s in students
    ], total
