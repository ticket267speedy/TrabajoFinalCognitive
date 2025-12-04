"""
Servicio de Estudiantes

Orquesta la lógica de negocio para operaciones con estudiantes.
Utiliza el repositorio para acceder a datos.
"""
from typing import Dict, Any, Optional, List
from ..repositories.students.students_repository import (
    get_all_students_repo,
    get_student_by_id_repo,
    create_student_repo,
    update_student_repo,
    delete_student_repo,
    get_student_courses_repo
)
from ..models import Student


class StudentService:
    """Servicio para gestionar estudiantes"""
    
    def get_all_students(self, limit: int = 50, offset: int = 0, course_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene todos los estudiantes con paginación"""
        try:
            students, total = get_all_students_repo(limit=limit, offset=offset, course_id=course_id)
            
            return {
                "ok": True,
                "data": [self._student_to_dict(s) for s in students],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener estudiantes: {str(e)}"
            }
    
    def get_student_by_id(self, student_id: int) -> Dict[str, Any]:
        """Obtiene un estudiante por ID"""
        try:
            student = get_student_by_id_repo(student_id)
            
            if not student:
                return {
                    "ok": False,
                    "message": f"Estudiante {student_id} no encontrado"
                }
            
            return {
                "ok": True,
                "data": self._student_to_dict(student)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener estudiante: {str(e)}"
            }
    
    def create_student(self, name: str, email: str, id_number: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Crea un nuevo estudiante"""
        try:
            if not name or not email or not id_number:
                return {
                    "ok": False,
                    "message": "name, email e id_number son requeridos"
                }
            
            student = create_student_repo(
                name=name,
                email=email,
                id_number=id_number,
                phone=phone
            )
            
            return {
                "ok": True,
                "id": student.id,
                "message": "Estudiante creado exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al crear estudiante: {str(e)}"
            }
    
    def update_student(self, student_id: int, **kwargs) -> Dict[str, Any]:
        """Actualiza datos de un estudiante"""
        try:
            student = update_student_repo(student_id, **kwargs)
            
            if not student:
                return {
                    "ok": False,
                    "message": f"Estudiante {student_id} no encontrado"
                }
            
            return {
                "ok": True,
                "message": "Estudiante actualizado exitosamente",
                "data": self._student_to_dict(student)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al actualizar estudiante: {str(e)}"
            }
    
    def delete_student(self, student_id: int) -> Dict[str, Any]:
        """Elimina un estudiante"""
        try:
            success = delete_student_repo(student_id)
            
            if not success:
                return {
                    "ok": False,
                    "message": f"Estudiante {student_id} no encontrado"
                }
            
            return {
                "ok": True,
                "message": "Estudiante eliminado exitosamente"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al eliminar estudiante: {str(e)}"
            }
    
    def get_student_courses(self, student_id: int) -> Dict[str, Any]:
        """Obtiene los cursos de un estudiante"""
        try:
            # Verificar que el estudiante existe
            student = get_student_by_id_repo(student_id)
            if not student:
                return {
                    "ok": False,
                    "message": f"Estudiante {student_id} no encontrado"
                }
            
            courses = get_student_courses_repo(student_id)
            
            return {
                "ok": True,
                "data": courses,
                "total": len(courses)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener cursos del estudiante: {str(e)}"
            }
    
    @staticmethod
    def _student_to_dict(student: Student) -> Dict[str, Any]:
        """Convierte un objeto Student a diccionario"""
        return {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "id_number": student.id_number,
            "phone": student.phone,
            "created_at": student.created_at.isoformat() if student.created_at else None
        }
