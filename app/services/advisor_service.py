"""
Servicio de Asesor de Becas

Orquesta la lógica de negocio para operaciones del perfil asesor.
Utiliza el repositorio para acceder a datos.
"""
from typing import Dict, Any, Optional, List
from ..repositories.advisors import (
    get_scholarship_students_repo,
    get_alerts_repo,
    mark_alert_read_repo,
    get_advisor_summary_repo
)
from ..models import Student, Alert


class AdvisorService:
    """Servicio para gestionar operaciones del perfil asesor de becas"""
    
    def get_scholarship_students(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Obtiene estudiantes becarios con paginación.
        
        Args:
            limit: Cantidad de resultados por página
            offset: Desplazamiento para paginación
            
        Returns:
            Diccionario con datos de estudiantes o error
        """
        try:
            students, total = get_scholarship_students_repo(limit=limit, offset=offset)
            
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
                "message": f"Error al obtener becarios: {str(e)}"
            }
    
    def get_alerts(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Obtiene alertas ordenadas por fecha (más recientes primero).
        
        Args:
            limit: Cantidad de resultados por página
            offset: Desplazamiento para paginación
            
        Returns:
            Diccionario con datos de alertas o error
        """
        try:
            alerts, total = get_alerts_repo(limit=limit, offset=offset)
            
            return {
                "ok": True,
                "data": [self._alert_to_dict(a) for a in alerts],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener alertas: {str(e)}"
            }
    
    def mark_alert_as_read(self, alert_id: int) -> Dict[str, Any]:
        """
        Marca una alerta como leída.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Diccionario con resultado de operación
        """
        try:
            success = mark_alert_read_repo(alert_id)
            
            if not success:
                return {
                    "ok": False,
                    "message": f"Alerta {alert_id} no encontrada"
                }
            
            return {
                "ok": True,
                "message": "Alerta marcada como leída"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al marcar alerta: {str(e)}"
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene resumen de estadísticas para el asesor.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            summary = get_advisor_summary_repo()
            
            return {
                "ok": True,
                "data": summary
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener resumen: {str(e)}"
            }
    
    @staticmethod
    def _student_to_dict(student: Student) -> Dict[str, Any]:
        """Convierte un estudiante a diccionario"""
        return {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "is_scholarship_student": student.is_scholarship_student
        }
    
    @staticmethod
    def _alert_to_dict(alert: Alert) -> Dict[str, Any]:
        """Convierte una alerta a diccionario"""
        student = alert.student if hasattr(alert, 'student') else None
        course = alert.course if hasattr(alert, 'course') else None
        
        alert_data = {
            "id": alert.id,
            "message": alert.message,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "is_read": alert.is_read,
            "student": {
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name
            } if student else None
        }
        
        if course:
            alert_data["course_id"] = course.id
            alert_data["course_name"] = course.name
        
        return alert_data
