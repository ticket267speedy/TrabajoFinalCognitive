"""
Servicio de Cursos

Orquesta la lógica de negocio para operaciones con cursos.
Utiliza el repositorio para acceder a datos.
"""
from typing import Dict, Any, Optional
from ..repositories.courses.courses_repository import (
    get_all_courses_repo,
    get_course_by_id_repo,
    create_course_repo,
    update_course_repo,
    delete_course_repo,
    enroll_student_repo,
    unenroll_student_repo,
    get_course_students_repo
)
from ..models import Course


class CourseService:
    """Servicio para gestionar cursos"""
    
    def get_all_courses(self, limit: int = 50, offset: int = 0, status: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene todos los cursos con paginación"""
        try:
            courses, total = get_all_courses_repo(limit=limit, offset=offset, status=status)
            
            return {
                "ok": True,
                "data": [self._course_to_dict(c) for c in courses],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener cursos: {str(e)}"
            }
    
    def get_course_by_id(self, course_id: int) -> Dict[str, Any]:
        """Obtiene un curso por ID"""
        try:
            course = get_course_by_id_repo(course_id)
            
            if not course:
                return {
                    "ok": False,
                    "message": f"Curso {course_id} no encontrado"
                }
            
            return {
                "ok": True,
                "data": self._course_to_dict(course)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener curso: {str(e)}"
            }
    
    def create_course(self, name: str, code: str, description: Optional[str] = None, 
                     instructor_id: Optional[int] = None, schedule: Optional[str] = None) -> Dict[str, Any]:
        """Crea un nuevo curso"""
        try:
            if not name or not code:
                return {
                    "ok": False,
                    "message": "name y code son requeridos"
                }
            
            course = create_course_repo(
                name=name,
                code=code,
                description=description,
                instructor_id=instructor_id,
                schedule=schedule
            )
            
            return {
                "ok": True,
                "id": course.id,
                "message": "Curso creado exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al crear curso: {str(e)}"
            }
    
    def update_course(self, course_id: int, **kwargs) -> Dict[str, Any]:
        """Actualiza datos de un curso"""
        try:
            course = update_course_repo(course_id, **kwargs)
            
            if not course:
                return {
                    "ok": False,
                    "message": f"Curso {course_id} no encontrado"
                }
            
            return {
                "ok": True,
                "message": "Curso actualizado exitosamente",
                "data": self._course_to_dict(course)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al actualizar curso: {str(e)}"
            }
    
    def delete_course(self, course_id: int) -> Dict[str, Any]:
        """Elimina un curso"""
        try:
            success = delete_course_repo(course_id)
            
            if not success:
                return {
                    "ok": False,
                    "message": f"Curso {course_id} no encontrado"
                }
            
            return {
                "ok": True,
                "message": "Curso eliminado exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al eliminar curso: {str(e)}"
            }
    
    def enroll_student(self, course_id: int, student_id: int) -> Dict[str, Any]:
        """Inscribe un estudiante en un curso"""
        try:
            enrollment = enroll_student_repo(course_id, student_id)
            
            if not enrollment:
                return {
                    "ok": False,
                    "message": "Error al inscribir estudiante (puede que ya esté inscrito)"
                }
            
            return {
                "ok": True,
                "message": "Estudiante inscrito exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al inscribir estudiante: {str(e)}"
            }
    
    def unenroll_student(self, course_id: int, student_id: int) -> Dict[str, Any]:
        """Desincribe un estudiante de un curso"""
        try:
            success = unenroll_student_repo(course_id, student_id)
            
            if not success:
                return {
                    "ok": False,
                    "message": f"Enrollment no encontrado"
                }
            
            return {
                "ok": True,
                "message": "Estudiante desincrito exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al desincribir estudiante: {str(e)}"
            }
    
    def get_course_students(self, course_id: int, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Obtiene los estudiantes de un curso"""
        try:
            # Verificar que el curso existe
            course = get_course_by_id_repo(course_id)
            if not course:
                return {
                    "ok": False,
                    "message": f"Curso {course_id} no encontrado"
                }
            
            students, total = get_course_students_repo(course_id, limit=limit, offset=offset)
            
            return {
                "ok": True,
                "data": students,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener estudiantes del curso: {str(e)}"
            }
    
    @staticmethod
    def _course_to_dict(course: Course) -> Dict[str, Any]:
        """Convierte un objeto Course a diccionario"""
        return {
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "description": course.description,
            "instructor_id": course.instructor_id,
            "schedule": course.schedule,
            "created_at": course.created_at.isoformat() if course.created_at else None
        }
